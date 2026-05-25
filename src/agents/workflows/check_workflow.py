# Copyright (c) 2025 ByteDance Ltd. and/or its affiliates
# SPDX-License-Identifier: Apache-2.0
import litellm

from src.agents.tools.code_act_tools import ExecuteBashTool, FinishTool, StrReplaceTool
from src.agents.workflows.base_workflow import BaseWorkflow, WorkflowConfig
from src.runtime.base_runtime import BaseRuntime
from src.task.bench_task import BenchTask
from loguru import logger
from copy import deepcopy


class CheckWorkflow(BaseWorkflow):
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
<BACKGROUND>
CSBench项目旨在将计算机大作业转换为可评估的基准测试。我们收集了来自各个开源课程的大作业，将其转换为测试用例。作为一个benchmark，CSBench的每一个case都是未完成的题目，包含脚手架代码和若干UT以及任务指令。
</BACKGROUND>

<ROLE>
你的角色是作为一个具有顶级PhD水准的计算机科学家，你将以严格的标准对标注员产出的代码进行审查。

你**不需要**完成题目，只需要检查任务文件是否make sense。
代码框架将不包含完整代码，甚至可能只包含pass语句。这是完全允许的。
你应当具有老练清晰的思维能力，不要盲目阅读，而是及时总结。
</ROLE>

<WORKFLOW>
0. 做最基本的sanity check，看看UT是否是占位符。若是，则可直接返回结果。
1. 首先结合下文即将给出的任务描述，理解任务的需求和功能
2. 阅读/testbed目录下的代码文件，分析代码框架的结构
3. 阅读tests/目录下的测试文件，仔细地检查每个测试的功能点
4. 评估task.md文件的质量：
    - 检查任务描述是否包含必要的信息，比如任务的背景、需求、功能点等。以及严重程度，比如缺少之后是否会导致难以理解题目。
    - 检查任务描述是否有错误或遗漏，比如提到了不存在的文件（可能是在制作benchmark过程中被转换了）。
    - 检查任务描述是否泄漏了答案，比如直接写了答案或者具体的实现细节。仅仅是指导实现方法是允许的。
**任务描述的质量**：
- 不要挑刺地追求完整性，不要过度追求长度，短小精练的任务描述一样优秀，只看信息点！
- 不要苛求完整的描述，但是要保证基本的完整性。

5. 将任务需求以及代码框架结合起来，评估UT的质量，常见问题包括：
    - 占位符：测试不涉及任何实际运行和任务相关的代码，直接assert False/True，或者运行了一些和题目完全无关的代码
    - 过于宽松：只检查了基本输入输出格式，或者数据边界值，完全没有检查具体功能
        - 例外：输入输出本身具有高度特异性，或者该任务就是只关注输出（典型如bomblab, 只检查炸弹的输出已经足以判断，所以应当认为足够）
    - 覆盖不足：有的功能完全没有检查，并且也没有在单测中被自然使用到。我们允许一定的覆盖率不足，但要求题目要求中的功能点必须覆盖到。
**打分要求**：
- 不要苛求异常处理
- 允许测试大量失败，因为这是脚手架代码
- 不要苛求边界条件检查，允许测试只检测常规流程
- 只要测试覆盖大部分题目功能点，并且不是特别宽松，就应该认为基本可用。
- 然而，如果已经宽松到即使内容完全错误也能通过测试（比如只检测矩阵乘法的形状、只检测概率位于[0, 1]等），则认为存在重大缺陷
</WORKFLOW>

<OUTPUT_SPECIFICATION>
一个/tmp/result.json文件，包含以下字段：
- md_eval
    - 缺乏关键信息: bool
    - 直接泄漏答案: bool
    - 包含不存在的文件: bool
    - 错误或遗漏: bool
    - 其他问题: str|None, 如有，简单描述还存在什么问题，否则为None
    - 整体评分：int, 0~3，分数越低越差。0分表示重大缺陷，1分表示存在问题，2分表示正确可用，3分表示完美。
    - summary: str, 总结任务描述的大纲、内容，100字左右。
    - comment: str, 简单对任务描述的质量、完整性进行评价，100字左右。
- qa_eval
    - 测试为占位符: bool
    - 只做基本检查过于宽松: bool
    - 覆盖不足: bool
    - 其他问题: str|None, 如有，简单描述还存在什么问题，否则为None
    - 整体评分：int, 0~3，分数越低越差。0分表示完全不相关的占位符，1分表示相关但存在重大缺陷，2分表示基本可用，能全pass的基本上不会hack（比如进行了特异性输入输出检查，或者进行了白盒测试），3分表示功能完整约束适当的测试。
    - summary: str, 总结测试的功能点，100字左右。
    - comment: str, 对测试的相关性、约束适宜性、覆盖度进行评价，200字左右。
</OUTPUT_SPECIFICATION>
"""


        USER_PROMPT = f"""待质检任务的任务描述位于/testbed/task.md，任务文件位于 /testbed. 确保一次只调用一个工具，并且在任务完成后调用 finish 工具。在你结束之前，确保你的输出文件/tmp/result.json可以被json.loads解析并且符合规范。
        """.strip()

        return [
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user', 'content': USER_PROMPT},
        ]
