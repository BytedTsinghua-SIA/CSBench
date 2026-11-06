# CSBench

[简体中文](./README.md) | [English](./README.en.md)

CSBench 是一个面向学术计算机课程任务的 Docker 基准框架，用来评估 coding agent 在真实代码仓库中的系统级端到端修复、实现和调试能力。

本仓库的 `main` 分支是完整的 Harbor 兼容发行版：它保留原始 CSBench 的任务、运行器、评测逻辑和文档，同时把同一批任务发布为 Harbor task schema 1.4。用户既可以复现论文使用的原始 CodeAct 流程，也可以在不改任务镜像的情况下使用 Harbor 内置或自定义 agent。

原始实验实现保留在 `origin_experiment` 分支，便于追溯历史实验；新用户建议从 `main` 开始。

## 两种运行方式

| 方式 | 适用场景 | 入口 |
|---|---|---|
| Harbor（推荐） | 使用统一 harness、更换 agent/scaffold、扩展后续实验 | `scripts/run_harbor.sh` |
| CSBench 原始运行器 | 严格复现原始 CodeAct prompt、工具和执行循环 | `main.py` / `run.py` |

两种方式共用 `tasks/` 中的任务定义和同一批 Docker 镜像。Harbor 直接引用预构建镜像，不需要增加 Harbor 专用镜像层。完整设计、支持的 agent 和验证方法见 [Harbor 使用说明](docs/HARBOR.zh-CN.md)。

## Harbor 快速上手

环境要求：Python 3.12+、Docker（含 Compose v2）。

```bash
git clone https://github.com/huiyeruzhou/HaneYuu.git CSBench
cd CSBench
scripts/bootstrap.sh
cp .env.example .env
```

在 `.env` 中填写模型服务后，可以运行单题或整个数据集：

```bash
CSBENCH_TASK=cs000280 scripts/run_harbor.sh  # 单题
scripts/run_harbor.sh                       # 全部任务
```

也可以直接调用 Harbor 的内置 agent。下面示例假设已按该 agent 的要求导出模型凭据：

```bash
.venv/bin/harbor run \
  --path dataset/csbench \
  --include-task-name cs000280 \
  --agent mini-swe-agent \
  --model openai/gpt-5.2
```

Codex 直接使用 Harbor 内置的 `--agent codex`，不需要 CSBench 自定义 agent。若容器不能直连 Codex 安装源，在 `.env` 中设置 `HTTP_PROXY` / `HTTPS_PROXY` 即可；入口脚本会用 Harbor 官方 `--agent-env` 参数把代理传给 setup 和 run 阶段。完整命令和 endpoint 注意事项见 [Harbor 使用说明](docs/HARBOR.zh-CN.md#codex-agent)。

`dataset/csbench/` 已包含可直接运行的 Harbor 任务；`scripts/generate_dataset.py` 可从本仓的原始任务重新生成它们。任务镜像统一使用 `docker.io/honglifish/csbench:<task-id>`，发布工具默认仅做 dry run。

### 多次运行、并发和命名

`scripts/run_harbor.sh` 会读取 `.env`，并把额外参数原样传给 Harbor。`-k` 是每题运行次数，`-n` 是全局并发 trial 数；它们都是 Harbor 官方参数：

```bash
# cs000280 跑 2 次，最多并发 8 个 trial
CSBENCH_TASK=cs000280 \
CSBENCH_JOB_NAME=gpt52-mini \
scripts/run_harbor.sh -k 2 -n 8
```

输出默认写入 `jobs/<job-name>/`。可通过 `CSBENCH_JOBS_DIR` 改输出根目录，通过 `CSBENCH_AGENT` 更换 agent。每组正式实验应使用唯一的 job name，隔离 smoke、模型和实验配置。

### 查看和汇总 Harbor 结果

Harbor 的官方网页查看器可以浏览 job、trial、agent trajectory、异常和 verifier 输出：

```bash
.venv/bin/harbor view jobs --jobs
```

单个 job 的 `result.json` 保存聚合状态，每个 trial 子目录中的 `result.json` 保存 task、agent/model、token/cost、异常和 verifier reward。`verifier/reward.txt` 是原始二值分数，`verifier/test-stdout.txt` 是测试输出。CSBench 额外提供一个只读汇总工具，将官方 JSON 展平为 CSV，并按 agent/model 计算通过率：

```bash
python3 scripts/summarize_harbor_results.py jobs/<job-name>
# 等价入口
make summarize JOB=jobs/<job-name>
```

结果写到 `jobs/<job-name>/analysis/trials.csv` 和 `summary.json`；传入整个 `jobs/` 时写到 `jobs/_analysis/`。运行和网页查看由 Harbor 官方 CLI 完成，CSV/JSON 汇总是本仓的辅助脚本。`harbor analyze` 是可选的、会额外调用模型的 trajectory 分析，不是计算基础分数所必需的步骤。

完整的输出目录、字段含义、官方工具与仓库脚本边界见 [Harbor 使用说明](docs/HARBOR.zh-CN.md)。

## 原始 CSBench 运行器快速上手

### 安装依赖

如果已经执行过 `scripts/bootstrap.sh`，生成的 `.venv` 同时包含 Harbor adapter 和原始运行器所需依赖，可以直接使用。若需要严格复现历史依赖（包括旧版 `httpx`），请使用独立环境，避免与 Harbor 的依赖冲突：

- 用 `uv` 安装

```bash
uv venv .venv-original --python 3.13
source .venv-original/bin/activate            # 激活原始实验环境
uv pip install -r requirements.txt            # 安装项目常用依赖
```

- 用 `pip` 安装

```bash
python -m venv .venv-original
source .venv-original/bin/activate
pip install -r requirements.txt     # 安装原始实验依赖
```

额外提供`requirements-freeze.txt`完整 freeze，作为复现实验环境的参考。

### 配置api

openai兼容的api提供商（如openrouter等）不需要修改PROVIDER。但使用responses api的azure模型需要修改PROVIDER为azure。

```sh
cat > .env <<EOF
PROVIDER="openai"
API_MODE="chat" # responses for latest GPT models
API_BASE = "https://xxx/v1"
API_KEY = "sk-xxxxxx"
API_MODEL="gpt-5.2"

OUTPUT_ROOT="."
DOCKER_REGISTRY="docker.io"
DOCKER_REPOSITORY="honglifish/csbench"
EOF
```

### 运行 benchmark

```bash
python3 main.py -n 3 -k 2             # 主入口：从 registry 拉取镜像并运行（不本地 build）
python3 read_report.py                # 汇总已有 reports/ 的结果
```

默认使用 `main.py` 时，会按顺序做这些事：

1. 为任务准备或复用 Docker 镜像
2. 调用 `scripts.run_agent` 在容器里运行 agent
3. 调用 `scripts.evaluate_patch` 回放 patch 并跑测试
4. 调用 `scripts.visualize_conversation` 产出对话可视化
5. 持续把结果写到 `reports/`，把阶段输出写到 `logs/`

`read_report.py` 会：
- 扫描 `reports/*.json`
- 根据 `task_name` 和 `attempt_id` 找回对应日志目录
- 统计 build / coldstart / run_agent / evaluate 的失败情况
- 检查 patch 是否为空
- 统计每个 task 在多次 attempt 下的通过次数分布
- 输出一些超时、异常和可疑样本，方便排查

跑完之后，通常看这几个位置：

- `logs/<task_name>/attempt<N>/`：过程日志、对话、patch
- `reports/<task_name>_attempt<N>.json`：结构化结果
- `tasks/<task_name>/`：任务源码与任务说明

### 测试多个模型

`ENV_FILE`环境变量可以用于指定自定义的环境文件。如果要运行多个模型，可以通过分别编写`.env.gpt`、`.env.glm`等文件，并修改`ENV_FILE`环境变量来实现。

下面两个任务可以并发运行（只要OUTPUT_ROOT不同）：

```bash
export ENV_FILE=.env.gpt
python3 run.py -k 1

export ENV_FILE=.env.glm
python3 run.py -k 1
```

## 主入口

### `main.py`

```bash
python3 main.py -n 10                           # 扫描任务目录并运行前 10 个任务
python3 main.py -n 50 -x 8 -k 2                 # 8 并发、每题 2 次 attempt
python3 main.py --task cs000007                 # 跑单个任务
python3 main.py --task cs000007 -k 3            # 同一个任务跑 3 个 attempt
python3 main.py --task "[cs000007,cs000008]"    # 指定多个任务
```

参数大意：

- `--task`：跑指定任务；不传时会扫描整个 `TASK_ROOT`
- `-n` / `--num-tasks`：限制要跑的任务数
- `-k` / `--pass-k`：每个任务跑多少次 attempt
- `-x`：并发 worker 数，太多会显著增加cpu和memory压力，建议不要超过memory / 4和cpu * 2
- `main.py` 会按顺序做这些事：

1. 为任务准备或复用 Docker 镜像
2. 调用 `scripts.run_agent` 在容器里运行 agent
3. 调用 `scripts.evaluate_patch` 回放 patch 并跑测试
4. 调用 `scripts.visualize_conversation` 产出对话可视化
5. 持续把结果写到 `reports/`，把阶段输出写到 `logs/`
其中公开镜像默认由 `.env` 中的 `DOCKER_REGISTRY` / `DOCKER_REPOSITORY` 解析为单仓库多 tag 布局（由 `src/config.py` 读取）；将 `DOCKER_REPOSITORY` 留空可切回历史的 namespace/task 布局。


工程细节：

- 用线程和共享状态避免同一个 task 的多个 attempt 重复做 “镜像准备阶段”
- 将每一步的 stdout/stderr 写到文件，避免长时间子进程因为管道阻塞卡死
- 在 Ctrl+C 时尽量优雅地停止未完成任务
- 用实时面板显示多任务并发时的执行状态

### `run.py`

`run.py` 是“本地 build 版本”：会先调用 `scripts/build_image.py` 把 task 的 Dockerfile + src staged 出一个 build context，然后进行 docker build，并做 coldstart（运行 `test.sh`）检查，再进入 agent/evaluate 等阶段。你需要本地 build 或要强制重建镜像时用它。

```bash
python3 run.py --task cs000007 --force-build
```


### `read_report.py`

```bash
python3 read_report.py
```

它读取 `reports/` 和 `logs/` 目录下的所有结果，进行结果归纳。

它会做的事情包括：

- 扫描 `reports/*.json`
- 根据 `task_name` 和 `attempt_id` 找回对应日志目录
- 统计 build / coldstart / run_agent / evaluate 的失败情况
- 检查 patch 是否为空
- 统计每个 task 在多次 attempt 下的通过次数分布
- 输出一些超时、异常和可疑样本，方便排查

常见命令：

```bash
python3 read_report.py                         # 读取默认 reports/ 目录
python3 read_report.py --report reports        # 显式指定报告目录
python3 read_report.py --attempts 2            # 按每题 2 次 attempt 统计通过率
```

### `.env` 配置

项目启动时会自动读取 `.env`。一个常见配置如下：

```env
# TASK_ROOT=tasks
# OUTPUT_ROOT=.
# BUILD_ROOT=build
# DOCKER_REGISTRY=docker.io
# DOCKER_REPOSITORY=honglifish/csbench

PROVIDER=openai
API_KEY=your_key
API_MODEL=your_model
API_BASE=
```

常用配置项说明：

- `TASK_ROOT`：任务文件的根目录
- `OUTPUT_ROOT`：日志与报告输出目录会是 `<OUTPUT_ROOT>/logs/` 和 `<OUTPUT_ROOT>/reports/`
- `BUILD_ROOT`：本地构建镜像时使用到的缓存目录
- `DOCKER_REGISTRY`：镜像仓库地址
- `DOCKER_REPOSITORY`：公开发布使用的共享 repository；每个任务使用自己的 task-ID tag。默认示例解析为 `docker.io/honglifish/csbench:cs000007`
- `DOCKER_NAMESPACE` / `DOCKER_TAG`：仅在 `DOCKER_REPOSITORY` 留空时使用，保留历史的 `<registry>/<namespace>/<task>:<tag>` 布局
- `PROVIDER` / `OPENAI_*`：LLM 提供方与模型配置，注意请永远使用OPENAI开头的前缀即使PROVIDER等于`anthropic`之类的。这些环境变量最终用于litellm的初始化。

## 目录约定

### `tasks/` （TASK_ROOT）

`tasks/` 是 benchmark 数据本体。每个任务通常长这样：

```text
tasks/<task_name>/
  src/
  metadata/
  entry_list.txt   # 可选的历史遗留文件；当前代码不再读取
```

其中：

- `src/`：任务源码，会被拷贝进镜像内的 `/testbed`
- `metadata/task.md`：任务说明，agent 会读取它来理解题目
- `metadata/Dockerfile`：任务专属镜像定义
- `metadata/test_override/`：评测阶段恢复的测试文件，用来防止 agent 篡改测试
- `entry_list.txt`：历史遗留的镜像名/base commit 映射文件；当前运行链路不再依赖它

### `logs/` （`OUTPUT_ROOT/logs/`）

`logs/` 保存每次 attempt 的完整过程。典型结构如下：

```text
logs/<task_name>/attempt<N>/
  1.docker_build.out
  1.docker_build.err
  2.coldstart.out              # 仅 `run.py`（本地 build 路径）会产出
  2.coldstart.err
  3.run_agent.out
  3.run_agent.err
  4.evaluate.out
  4.evaluate.err
  5.transform.out
  5.transform.err
  conversation_history.json
  patch
  testbed.zip                 # 仅在 --archive-testbed 时生成
```

最值得关注的文件有：

- `conversation_history.json`：完整对话轨迹
- `patch`：agent 生成的最终 git patch
- `*.out` / `*.err`：每个阶段的标准输出和错误输出
- `testbed.zip`：可选导出的评测现场快照

### `reports/` （`OUTPUT_ROOT/reports/`）

`reports/` 保存结构化结果，每个 attempt 一个 JSON：

```text
reports/<task_name>_attempt<N>.json
```

这里通常会记录：

- 各阶段是否成功
- 各阶段耗时
- 各阶段 stdout / stderr 摘要
- 最终评测结果

### `build/` （BUILD_ROOT）

`build/` 是 Docker 构建上下文的 staging 目录。每个任务会在这里生成：

```text
build/<task_name>/
build/<task_name>.lock
```

含义分别是：

- `build/<task_name>/`：临时构建上下文
- `build/<task_name>.lock`：防止并发构建同一任务的锁文件


## `scripts/` 模块

这里放的是可以单独执行的辅助脚本。

### `scripts/build_image.py`

基本用法：

```bash
python3 -m scripts.build_image <task_name>
```

常见命令：

```bash
python3 -m scripts.build_image cs000007                   # 本地构建镜像
python3 -m scripts.build_image cs000007 --force           # 强制重建镜像
python3 -m scripts.build_image cs000007 --use-pip-mirror  # 为 pip 安装阶段启用镜像源
python3 -m scripts.build_image cs000007 --push            # 构建成功后推送镜像
```

### `scripts/run_agent.py`

基本用法：

```bash
python3 -m scripts.run_agent code_act_agent <task_name> <log_tag>
```

常见命令：

```bash
python3 -m scripts.run_agent code_act_agent cs000007 attempt0  # 单独运行一次 agent
```

### `scripts/evaluate_patch.py`

基本用法：

```bash
python3 -m scripts.evaluate_patch <task_name> <attempt_id>
```

常见命令：

```bash
python3 -m scripts.evaluate_patch cs000007 0                    # 回放 patch 并执行测试
python3 -m scripts.evaluate_patch cs000007 0 --archive-testbed  # 额外导出 testbed.zip 方便排查
```

### `scripts/visualize_conversation.py`

基本用法：

```bash
python3 -m scripts.visualize_conversation <conversation_history.json>
```

常见命令：

```bash
python3 -m scripts.visualize_conversation logs/cs000007/attempt0/conversation_history.json  # 转成可视化 HTML
```

## 源码架构

### 怎么读代码（推荐顺序）

1. 先看 `run.py`：它是一个“状态管理 + 命令行驱动器”。每个 step（build/coldstart/run_agent/evaluate/transform）都被包装成可记录状态、可复用、可并发的 Runner 步骤，并把 stdout/stderr 落盘到 `logs/`，同时把结构化结果写到 `reports/`。`main.py` 复用了这一套 Runner/并发/UI，只是把镜像准备阶段改成了 pull。
2. 再看 `scripts/`：这些是真正干活的子命令（例如 `scripts.run_agent` / `scripts.evaluate_patch`），它们才是流程的业务核心。
3. 最后看 `src/`：`BenchTask`/runtime/agents 等是抽象层，负责把 task 映射到镜像与 repo、把容器操作封装成 runtime、把 agent workflow 封装成可替换策略。

### `main.py` vs `run.py` 的区别

- `main.py`：pull 镜像版本（默认入口）。复用 `run.py` 的 Runner/并发/日志面板/落盘逻辑，只覆写“镜像准备阶段”：用 `docker pull` 代替本地 build；同时跳过 coldstart（直接标记成功）。
- `run.py`：本地 build 版本。会 build 并做 coldstart，更适合你在本地制作/更新 task 镜像。

### `run.py` 的设计理念（为什么不是几行命令就完了）

确实可以几行命令就把流程跑起来，例如：准备镜像 → 起容器跑 agent → 回放 patch 跑测试。但那样会丢掉基准跑批真正需要的工程能力：并发调度、跨 attempt 共享 setup、可中断的子进程管理、每一步的 stdout/stderr 落盘、防止管道堵塞、实时状态面板、以及 `reports/` 的结构化结果（后续 `read_report.py` 才能自动归纳/排查）。


### `src/config.py`

统一管理全局路径和环境变量，例如：

- `TASK_ROOT`
- `OUTPUT_ROOT`
- `BUILD_ROOT`
- `DOCKER_REGISTRY`
- `DOCKER_REPOSITORY`
- `DOCKER_NAMESPACE`

### `src/task/`

任务抽象层。`BenchTask` 负责：

- 读取 `metadata/task.md`
- 根据 `DOCKER_REGISTRY` / `DOCKER_REPOSITORY` 解析公开的单仓库多 tag 镜像引用，同时兼容历史的 `DOCKER_NAMESPACE` / `DOCKER_TAG` 布局
- 在镜像内执行 `git rev-parse HEAD`，把 `/testbed` 的 `HEAD` 作为 `base_commit`
- 提供 task 对应的日志路径等辅助能力

### `src/runtime/`

容器运行时抽象。`LocalDockerContainerRuntime` 负责：

- 启停 Docker 容器
- 在容器里执行命令
- 在宿主机和容器之间传文件
- 支持更复杂的交互式 screen / attach 场景

### `src/agents/`

agent 主体实现，主要分成三层：

- `workflows/`：工作流编排，控制一轮 agent 如何推进
- `tools/`：agent 可调用工具
- `utils/llm.py`：LLM 配置与模型接入

## FAQ

### 构建卡住在锁上怎么办？

锁文件默认在 `build/<task_name>.lock`。确认没有对应构建进程后，可以手动删除这个锁文件。

### 怎么切换任务目录、输出目录或镜像仓库？

直接修改 `.env`，例如：

```env
TASK_ROOT=/path/to/tasks
OUTPUT_ROOT=/path/to/output
BUILD_ROOT=/path/to/build-root
DOCKER_REGISTRY=your-registry.example.com
DOCKER_REPOSITORY=your-namespace/csbench
```
