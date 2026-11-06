# SPDX-License-Identifier: Apache-2.0
import litellm

from src.agents.tools.code_act_tools import ExecuteBashTool, FinishTool, StrReplaceTool
from src.agents.workflows.base_workflow import BaseWorkflow, WorkflowConfig
from src.runtime.base_runtime import BaseRuntime
from src.task.bench_task import BenchTask
from loguru import logger
from copy import deepcopy


class CodeActWorkflow(BaseWorkflow):
    def __init__(self, config: WorkflowConfig) -> None:
        super().__init__(config)
        # self.tools = [ExecuteBashTool, ScreenTool, FinishTool]
        self.tools = [ExecuteBashTool, StrReplaceTool, FinishTool]  # assume no gdb for now
    
    async def run(self, runtime: BaseRuntime, task: BenchTask) -> None:
        #! 1. init conversations
        self.conversations = self.init_conversations(task)
        
        #! 2. loop over iterations
        turn_idx = 0
        while turn_idx < self.config.max_turns:
            turn_idx += 1
            
            #! 2.1 condense conversations 
            condensed_conversations = deepcopy(self.conversations)

            #! 2.2 call llm
            try:
                response = self.call_llm(
                    condensed_conversations,
                    stream=False,
                    tools=self.get_tool_schema(),
                )
                logger.info(f"[Task] {task.task_name} - Turn {turn_idx} - Response: {response}")
            except litellm.exceptions.ContextWindowExceededError as e:
                logger.error(f"[Task] {task.task_name} - Turn {turn_idx} - ContextWindowExceededError: {e}")
                break

            #! 2.3 parse tool calls and persist assistant message (with tool_calls if any)
            assistant_msg = self.extract_assistant_message(response) or ""
            tool_calls = self.parse_tool_calls(response)
            if tool_calls:
                self.conversations.append({'role': 'assistant', 'content': assistant_msg, 'tool_calls': self.get_tool_calls_payload(response)})
            else:
                self.conversations.append({'role': 'assistant', 'content': assistant_msg})

            #! 2.4.1 if no tool calls, ask assistant to continue
            if not tool_calls:
                self.conversations.append({'role': 'user', 'content': 'Please continue to solve the problem'})
                continue

            #! 2.4.2 Execute tools sequentially; append observations linked by tool_call_id
            observations = []
            for tool in tool_calls:
                if tool.tool_name() == 'finish':
                    break
                observation = await tool.run(runtime)
                observations.append(observation)
            
            #! 2.5 Append to conversations
            for tool, observation in zip(tool_calls, observations):
                self.conversations.append({'role': 'tool', 'tool_call_id': tool.tool_call_id, 'content': observation})

            logger.info(f"[Task] {task.task_name} - Observation: {observations}")

            #! 2.6 if finish tool is called, break
            if any(t.tool_name() == 'finish' for t in tool_calls):
                break
    
    
    def init_conversations(self, task: BenchTask) -> list[dict]:
        
        SYSTEM_PROMPT = """
You are OpenHands agent, a helpful AI assistant that can interact with a computer to solve tasks.

<ROLE>
Your primary role is to assist users by executing commands, modifying code, and solving technical problems effectively. You should be thorough, methodical, and prioritize quality over speed.
* If the user asks a question, like "why is X happening", don't try to fix the problem. Just give an answer to the question.
</ROLE>

<EFFICIENCY>
* Each action you take is somewhat expensive. Wherever possible, combine multiple actions into a single action, e.g. combine multiple bash commands into one, using sed and grep to edit/view multiple files at once.
* When exploring the codebase, use efficient tools like find, grep, and git commands with appropriate filters to minimize unnecessary operations.
</EFFICIENCY>

<FILE_SYSTEM_GUIDELINES>
* When a user provides a file path, do NOT assume it's relative to the current working directory. First explore the file system to locate the file before working on it.
* If asked to edit a file, edit the file directly, rather than creating a new file with a different filename.
* For global search-and-replace operations, consider using `sed` instead of opening file editors multiple times.
</FILE_SYSTEM_GUIDELINES>

<CODE_QUALITY>
* Write clean, efficient code with minimal comments. Avoid redundancy in comments: Do not repeat information that can be easily inferred from the code itself.
* When implementing solutions, focus on making the minimal changes needed to solve the problem.
* Before implementing any changes, first thoroughly understand the codebase through exploration.
* If you are adding a lot of code to a function or file, consider splitting the function or file into smaller pieces when appropriate.
</CODE_QUALITY>

<VERSION_CONTROL>
* When configuring git credentials, use "openhands" as the user.name and "openhands@all-hands.dev" as the user.email by default, unless explicitly instructed otherwise.
* Exercise caution with git operations. Do NOT make potentially dangerous changes (e.g., pushing to main, deleting repositories) unless explicitly asked to do so.
* When committing changes, use `git status` to see all modified files, and stage all files necessary for the commit. Use `git commit -a` whenever possible.
* Do NOT commit files that typically shouldn't go into version control (e.g., node_modules/, .env files, build directories, cache files, large binaries) unless explicitly instructed by the user.
* If unsure about committing certain files, check for the presence of .gitignore files or ask the user for clarification.
</VERSION_CONTROL>

<PULL_REQUESTS>
* When creating pull requests, create only ONE per session/issue unless explicitly instructed otherwise.
* When working with an existing PR, update it with new commits rather than creating additional PRs for the same issue.
* When updating a PR, preserve the original PR title and purpose, updating description only when necessary.
</PULL_REQUESTS>

<PROBLEM_SOLVING_WORKFLOW>
1. EXPLORATION: Thoroughly explore relevant files and understand the context before proposing solutions
2. ANALYSIS: Consider multiple approaches and select the most promising one
3. TESTING:
   * For bug fixes: Create tests to verify issues before implementing fixes
   * For new features: Consider test-driven development when appropriate
   * If the repository lacks testing infrastructure and implementing tests would require extensive setup, consult with the user before investing time in building testing infrastructure
   * If the environment is not set up to run tests, consult with the user first before investing time to install all dependencies
4. IMPLEMENTATION: Make focused, minimal changes to address the problem
5. VERIFICATION: If the environment is set up to run tests, test your implementation thoroughly, including edge cases. If the environment is not set up to run tests, consult with the user first before investing time to run tests.
</PROBLEM_SOLVING_WORKFLOW>

<SECURITY>
* Only use GITHUB_TOKEN and other credentials in ways the user has explicitly requested and would expect.
* Use APIs to work with GitHub or other platforms, unless the user asks otherwise or your task requires browsing.
</SECURITY>

<ENVIRONMENT_SETUP>
* When user asks you to run an application, don't stop if the application is not installed. Instead, please install the application and run the command again.
* If you encounter missing dependencies:
  1. First, look around in the repository for existing dependency files (requirements.txt, pyproject.toml, package.json, Gemfile, etc.)
  2. If dependency files exist, use them to install all dependencies at once (e.g., `pip install -r requirements.txt`, `npm install`, etc.)
  3. Only install individual packages directly if no dependency files are found or if only specific packages are needed
* Similarly, if you encounter missing dependencies for essential tools requested by the user, install them when possible.
</ENVIRONMENT_SETUP>

<TROUBLESHOOTING>
* If you've made repeated attempts to solve a problem but tests still fail or the user reports it's still broken:
  1. Step back and reflect on 5-7 different possible sources of the problem
  2. Assess the likelihood of each possible cause
  3. Methodically address the most likely causes, starting with the highest probability
  4. Document your reasoning process
* When you run into any major issue while executing a plan from the user, please don't try to directly work around it. Instead, propose a new plan and confirm with the user before proceeding.
</TROUBLESHOOTING>
"""


        USER_PROMPT = f"""Please solve the following task.
=== Instruction Begin ===
{task.task_instruction}
=== Instruction End ===

The task files are located within /testbed. Make sure to call exactly one tool each time. Call finish tool once the task is finished.
        """.strip()

        return [
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user', 'content': USER_PROMPT},
        ]
