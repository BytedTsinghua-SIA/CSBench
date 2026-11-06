# 在 Harbor 中运行 CSBench

[简体中文](HARBOR.zh-CN.md) | [English](HARBOR.md)

本仓库同时包含原始 CSBench 实现和 Harbor 兼容层。兼容层由三部分组成：

1. 将原始 CodeAct workflow 接入 Harbor 的 external-agent adapter；
2. 将 100 个 CSBench 任务表示为 Harbor task schema 1.4 的数据集；
3. 只做镜像重新打 tag 和发布、绝不重新构建镜像的发布脚本。

## 镜像为什么不需要重建

Harbor 可以通过 `[environment].docker_image` 直接运行预构建镜像，并在运行时挂载 `/logs`、上传 verifier 到 `/tests`、设置工作目录。CSBench 镜像本身已经在 `/testbed` 中提供 Git checkout，并包含 `sh` 和 `bash`，因此满足 Harbor 的运行约定。

发布时采用一一对应的 tag 映射：

```text
<existing-source-repository>/cs000003:latest
    -> docker.io/honglifish/csbench:cs000003
```

`scripts/publish_images.py` 不包含任何 build 命令，只会在显式确认后执行 `docker image inspect`、`docker image tag` 和 `docker image push`，并检查打 tag 前后的 image ID 完全一致。

## 安装

需要 Python 3.12+、Docker（含 Compose v2）和 Harbor 0.20.x。

```bash
git clone https://github.com/huiyeruzhou/HaneYuu.git CSBench
cd CSBench
scripts/bootstrap.sh
cp .env.example .env
```

默认情况下 `CSBENCH_ROOT` 就是当前仓库，不需要另外下载原始 CSBench。若要测试本地 Harbor 源码，可在运行 bootstrap 前设置 `HARBOR_SOURCE=/absolute/path/to/harbor`。

Harbor 当前依赖较新的 `httpx`，而原始实验环境曾固定 `httpx==0.23.1`。`scripts/bootstrap.sh` 为 Harbor 创建独立的 `.venv` 并保留新版本依赖，避免破坏 Harbor；原始实验的 freeze 仍保存在 `requirements-freeze.txt` 中供追溯。

入口脚本使用以下配置：

| 变量 | 含义 |
|---|---|
| `API_MODEL`、`API_KEY`、`API_BASE`、`PROVIDER` | 原始 CSBench adapter 使用的模型和 endpoint |
| `CSBENCH_DATASET_DIR` | Harbor 数据集路径，默认 `dataset/csbench` |
| `CSBENCH_JOBS_DIR` | 结果根目录，默认 `jobs` |
| `CSBENCH_CONCURRENCY` | 默认并发 trial 数，默认 `4` |
| `CSBENCH_AGENT` | agent 名称或 import path，默认使用 CSBench CodeAct adapter |
| `CSBENCH_TASK` | 可选 task ID，例如 `cs000280` |
| `CSBENCH_JOB_NAME` | 可选的稳定输出 job name |

兼容标准 OpenAI 风格环境变量的集成也可以使用 `OPENAI_MODEL`、`OPENAI_API_KEY` 和 `OPENAI_API_BASE`。Harbor 内置 Codex 使用 `OPENAI_API_KEY` 和 `OPENAI_BASE_URL`。不要把填入密钥的 `.env` 提交到仓库。

## 配置并运行

复制 `.env.example`，至少填写模型名、API key 和 endpoint。运行原始 CSBench CodeAct agent：

```bash
CSBENCH_TASK=cs000280 scripts/run_harbor.sh  # 单题 smoke/功能验证
scripts/run_harbor.sh                       # 全量
```

等价的直接命令是：

```bash
.venv/bin/harbor run \
  --path dataset/csbench \
  --env-file .env \
  --agent csbench_harbor.agent:CSBenchCodeActAgent \
  --model openai/gpt-5.2 \
  --n-concurrent 4
```

这个 adapter 复用原始 prompt、工具、模型调用和 turn loop；Harbor 只负责容器生命周期、日志和任务调度。

本地数据集筛选参数使用裸 ID `cs000280`；写入结果后，Harbor 会加上数据集来源前缀，trial 的 `task_name` 为 `csbench/cs000280`。两者不要混用。

## 使用其他 Harbor agent

生成的数据集是标准 Harbor task，因此不依赖 CSBench adapter。示例：

```bash
.venv/bin/harbor run \
  --path dataset/csbench \
  --include-task-name cs000280 \
  --agent mini-swe-agent \
  --model openai/gpt-5.2
```

Harbor 0.20 暴露的相关 agent/scaffold 包括：

- 通用 coding loop：`aider`、`cline-cli`、`deerflow`、`goose`、`langgraph`、`mini-swe-agent`、`opencode`、`openhands`、`openhands-sdk`、`swe-agent`、`terminus`、`terminus-1`、`terminus-2`、`trae-agent`；
- 模型或厂商 CLI：`antigravity-cli`、`claude-code`、`codex`、`copilot-cli`、`cursor-cli`、`gemini-cli`、`kimi-cli`、`qwen-coder`、`rovodev-cli`；
- 其他打包 agent：`computer-1`、`devin`、`dspy-rlm`、`eve`、`grok-build`、`hermes`、`mimo`、`nemo-agent`、`nop`、`openclaw`、`oracle`、`pi`、`vibe`。

这份列表表示 Harbor 0.20 接口层面的兼容能力，不表示本仓逐一安装或验证了每个 agent；部分 agent 需要各自的 extra、CLI 或凭据。Harbor 还接受自定义 Python import path（`module.path:ClassName`）和 ACP registry 简写（`acp:<agent>`）。

### Codex agent

CSBench 不提供也不要求自定义 Codex adapter。Harbor 内置的 `codex` agent 会安装 OpenAI 官方 Codex CLI、执行任务，并把原生 trajectory 转为 ATIF。标准运行方式是：

```bash
CSBENCH_AGENT=codex \
CSBENCH_TASK=cs000003 \
scripts/run_harbor.sh -k 1 -n 1 \
  --agent-kwarg reasoning_effort=medium \
  --agent-kwarg web_search=disabled
```

直接使用 Harbor CLI 时，官方 Codex adapter 从宿主环境读取 `OPENAI_API_KEY`，可选读取 `OPENAI_BASE_URL`；模型由 `--model` 指定。`OPENAI_BASE_URL` 应填写 API 根地址，不要包含 Codex 会自行追加的 `/responses`。也可以选择用 `CODEX_AUTH_JSON_PATH`，或用 `CODEX_FORCE_AUTH_JSON=true` 复用宿主机 `~/.codex/auth.json`。

Harbor 的 `--env-file` 负责把 `.env` 加载到宿主进程；需要进入容器的网络代理应使用官方 `--agent-env` / `--ae` 传递。使用 wrapper 时只需在 `.env` 中设置 `HTTP_PROXY`、`HTTPS_PROXY`（或小写版本），脚本会自动转交。等价的纯 Harbor 命令如下；单引号会让 Harbor 从宿主环境解析变量，而不是把代理地址固化进 job 配置：

```bash
.venv/bin/harbor run \
  --path dataset/csbench \
  --include-task-name cs000003 \
  --env-file .env \
  --agent codex \
  --model gpt-5.3-codex \
  --agent-env 'HTTP_PROXY=${HTTP_PROXY}' \
  --agent-env 'HTTPS_PROXY=${HTTPS_PROXY}' \
  --agent-kwarg reasoning_effort=medium \
  --agent-kwarg web_search=disabled
```

如果环境没有代理，不要添加这两个 `--agent-env` 参数。可先加 `--install-only` 做零模型调用的安装兼容性检查。本仓已在未修改的 `cs000003` 镜像上验证：仅通过上述代理参数，Harbor 0.20 的内置 `codex` 在约 1 分钟内完成安装，0 exception；不需要重建镜像或加载本仓 Python agent。

为了兼容原始 CSBench `.env`，`scripts/run_harbor.sh` 会把 `API_KEY` / `API_BASE` 映射为 Codex 所需的标准变量，并移除 `API_BASE` 末尾多余的 `/responses`。这只是入口便利功能；直接调用 Harbor 时应优先使用上面的官方变量。

## 多次运行和并发

`scripts/run_harbor.sh` 读取 `.env`、设置 CSBench 的稳定默认值，并把额外参数原样传给 Harbor 官方 CLI。Harbor 的 `-k` 控制每题尝试次数，`-n` 控制全局并发 trial 数：

```bash
CSBENCH_TASK=cs000280 \
CSBENCH_JOB_NAME=gpt52-mini \
scripts/run_harbor.sh -k 2 -n 8
```

对应的长参数是 `--n-attempts 2` 和 `--n-concurrent 8`。用 `CSBENCH_JOBS_DIR` 修改输出根目录，用 `CSBENCH_AGENT` 更换 agent。每个需要比较的模型或配置应使用唯一 job name。

## 数据格式和 verifier

`dataset/csbench/<task-id>/` 的结构如下：

```text
cs000280/
├── environment/
│   └── .harbor-environment-placeholder
├── instruction.md
├── task.toml
└── tests/
    ├── test.sh
    └── test_override/...
```

Harbor 0.20 即使使用预构建镜像也要求存在 `environment/`。零字节 placeholder 仅用于让 Git 保存这个目录，运行时会立即删除；它不会产生镜像层或触发构建。

Verifier 会从任务 base commit 恢复 `test.sh` 和 `tests/`，应用发布的 protected-test override，再执行原始 `test.sh`，把二值 reward 写入 `/logs/verifier/reward.txt`。这与原始 evaluator 在新容器中保护测试面的行为一致。

已生成的数据集随仓发布。需要重新生成时运行：

```bash
.venv/bin/python scripts/generate_dataset.py --overwrite
```

公开分支不依赖私有实验目录；若不存在 `exp/out.csv`，生成器会使用已签入数据集中的公开 metadata catalog。

## 结果格式、查看与分析

磁盘上的结果格式由 Harbor 官方定义。一个完成的 job 结构如下：

```text
jobs/<job-name>/
├── config.json
├── lock.json
├── result.json                 # job 级计数、eval、token 和费用
├── job.log
└── <trial-name>/
    ├── config.json
    ├── lock.json
    ├── result.json             # task、agent/model、耗时、reward、异常
    ├── trial.log
    ├── artifacts/manifest.json
    └── verifier/
        ├── reward.txt          # CSBench 原始二值分数：1 或 0
        └── test-stdout.txt     # 原始测试输出
```

job 级 `result.json` 包含 `n_total_trials` 和 `stats`，后者记录完成/报错 trial 数、`evals`、token 总量与 `cost_usd`。trial 级 `result.json` 包含 `task_name`、`agent_info`、`agent_result`、`verifier_result`、`exception_info`、时间戳和各阶段结果。对 CSBench 而言，`verifier_result.rewards.reward == 1` 表示规范测试全部通过，`0` 表示未通过；异常单独记录，不能只看 reward 推断。

使用 Harbor 官方网页查看器交互式查看 job、trajectory、异常和 verifier 输出：

```bash
.venv/bin/harbor view jobs --jobs
# Harbor 会输出本地访问地址；默认端口范围从 8080 开始。
```

使用本仓的只读脚本生成数值汇总和表格：

```bash
python3 scripts/summarize_harbor_results.py jobs/<job-name>
make summarize JOB=jobs/<job-name>  # 等价快捷入口
```

输入单个 job 时，脚本生成 `analysis/trials.csv` 和 `analysis/summary.json`；输入整个 `jobs/` 时，生成 `jobs/_analysis/` 并汇总其中的直接子 job。CSV 每个 trial 一行；JSON 给出整体和各 agent/model 的 trial 数、有效分数数、通过数、通过率、平均 reward、异常数、token 和费用。脚本不会修改或上传 Harbor job。

工具边界如下：

- Harbor 官方：`harbor run` / `harbor job start`、`harbor view`、job/trial `result.json`、日志与 verifier 产物；
- CSBench 辅助脚本：`scripts/run_harbor.sh` 负责配置，`smoke_test.sh` 负责隔离验证，`summarize_harbor_results.py` 负责 CSV/JSON；
- Harbor 可选功能：`harbor analyze <job-or-trial>` 会额外调用一个模型分析 trajectory，消耗 API 预算，计算基础分数和汇总并不需要它；`harbor upload` 会向外部服务写入结果，本仓辅助脚本绝不会调用它。

不要把 `.smoke/jobs/` 与正式实验合并。`nop` smoke 不修改代码，reward 通常应为 0；此时应关注异常数为 0，它证明任务加载、容器和 verifier 链路正常。

## 隔离的 smoke test

```bash
make smoke TASK=cs000280        # Harbor/container/verifier 路径，不调用模型
make smoke-agent TASK=cs000280  # 一次真实 CodeAct trial
```

smoke 默认使用 `docker.io/honglifish/csbench:<task-id>`。如需验证等价的本地镜像，可显式指定内容不变的镜像映射：

```bash
SMOKE_IMAGE_TEMPLATE='registry.example/csbench/{task_id}:latest' \
make smoke TASK=cs000280
```

所有 smoke 产物都写到被忽略的 `.smoke/`，并标记为 `NON-PAPER / NON-REPORTABLE`，不能并入论文结果。

## 准备 Docker Hub 发布

源仓库必须通过参数或 `CSBENCH_SOURCE_REPOSITORY` 显式提供。下面的命令是 dry run，不执行任何 Docker 操作：

```bash
python scripts/publish_images.py \
  --source-repository registry.example/csbench
```

真实发布有双重保护，只允许目标 `docker.io/honglifish/csbench`：

```bash
python scripts/publish_images.py \
  --source-repository registry.example/csbench \
  --execute \
  --confirm-target docker.io/honglifish/csbench
```
