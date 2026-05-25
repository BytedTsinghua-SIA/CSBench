# Machine Learning Course 2025 HW2

## Task Description

Given the survey results from the past two days in a specific state in the U.S., predict the probability of testing positive on day 3.

**Evaluation Metric**: Mean Squared Error (MSE)

## Data

- All input data is stored in the data directory (specified in configuration)
- The dataset includes:
  - `train.csv`: Training data with target column
  - `test.csv`: Testing data (does NOT have the target column)
  - `sample_submission.csv`: Sample submission format
- You must save the predictions for the testing set to `/content/submission.csv`

## Framework

This assignment uses the AIDE (AI-Driven Exploration in the Space of Code) framework. The codebase is based on the [aideml](https://github.com/WecoAI/aideml) project with modifications.

## Implementation Requirements

You need to complete the following TODO sections in the provided notebook:

### 1. LLM Selection

- Try different LLM models
- Resources:
  - Hugging Face GGUF models: https://huggingface.co/models?library=gguf
  - OpenLLM Leaderboard: https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard
- Note: When copying links from Hugging Face, remember to replace 'blob' with 'resolve'

### 2. Agent Draft Method (`_draft`)

- Implement the logic to ask the LLM agent to come up with a solution for the machine learning task and implement it in Python
- The agent should:
  - Understand the task goal
  - Access data from the specified directory
  - Generate a plan and corresponding Python code
  - Save predictions to `/content/submission.csv`

### 3. Agent Improve Method (`_improve`)

- Implement the logic to ask the LLM agent to improve existing solution drafts
- The agent should consider:
  - Task description
  - Memory/summary of previous attempts
  - Previous solution code

### 4. Agent Debug Method (`_debug`)

- Implement the logic to ask the LLM agent to debug buggy implementations
- The agent should analyze:
  - Task description
  - Previous (buggy) implementation code
  - Execution output/errors
  - Data preview

### 5. Execution Result Parsing (`parse_exec_result`)

- Implement the logic to extract evaluation results from execution output
- The agent should:
  - Analyze the task, code implementation, and execution output
  - Extract the validation metric (MSE)
  - Determine if the code is buggy
  - Provide analysis/feedback
- You can force the LLM to structure the output to extract the metric
- Reference for structured output: https://python.useinstructor.com/integrations/llama-cpp-python/#llama-cpp-python

### 6. Feature Selection (`preview_csv`)

- Enhance the function to tell LLM agents which features are useful for prediction
- Currently, the function only lists column names
- You should provide more informative feature descriptions to help the agent make better decisions

## Technical Details

### Code Execution

- The `Interpreter` class executes code in a separate process and captures output
- Code execution has a timeout limit (default: 3600 seconds)
- Execution results include terminal output, execution time, and exception information

### Solution Tree

- The framework uses a tree structure (`Journal` and `Node`) to manage solution exploration
- Each `Node` contains:
  - Code and plan
  - Execution results
  - Evaluation metrics
  - Bug status
- Nodes can be in different stages: "draft", "debug", or "improve"

### Agent Search Policy

- The agent uses a search policy to decide whether to:
  - Draft a new solution
  - Debug a buggy solution
  - Improve an existing good solution
- Configuration parameters:
  - `num_drafts`: Number of drafts to generate before improving/debugging
  - `debug_prob`: Probability of choosing to debug vs improve
  - `steps`: Total number of iterations

### LLM Integration

- The framework uses `llama-cpp-python` for LLM inference
- The `generate_response` function handles LLM calls with:
  - System and user messages
  - Temperature set to 0 for reproducibility
  - Max tokens limit
  - Stop sequences

## Configuration

The configuration includes:

- Experiment name
- Data directory path
- Task goal description
- Agent parameters (steps, search policy settings)

## Output

The framework saves:

- `best_solution.py`: The best solution found
- `good_solution_{i}.py`: All good (non-buggy) solutions

## Important Notes

- Make a copy before running or editing the code
- The Interpreter cell should NOT be modified
- Before changing LLM, restart the session
- The testing file does NOT have the target column
- Predictions must be saved to `/content/submission.csv`
