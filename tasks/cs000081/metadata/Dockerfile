FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive \
    TZ=Etc/UTC \
    TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD=1

# 基础工具链与调试工具（x86_64）
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       gcc \
       gdb \
       binutils \
       make \
       python3 \
       python3-pip \
       python3-dev \
       file \
       git \
       curl \
       ca-certificates \
       vim \
       less \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir \
    pytest \
    torch==2.8.0 \
    torch-geometric==2.7.0 \
    networkx==3.4.2 \
    matplotlib==3.10.7 \
    numpy==2.2.6 \
    scikit-learn==1.7.2

RUN pip3 install --no-cache-dir torch_sparse torch_scatter

RUN pip3 install --no-cache-dir deepsnap

# 可选：GDB 默认使用 Intel 汇编风格（更贴合 Attack Lab 文档）
RUN mkdir -p /etc/gdb \
    && echo "set disassembly-flavor intel" > /etc/gdb/gdbinit

# 创建非 root 用户，方便在容器内编译与调试
ARG USERNAME=student
ARG USER_UID=1000
ARG USER_GID=1000
RUN groupadd --gid ${USER_GID} ${USERNAME} \
    && useradd --uid ${USER_UID} --gid ${USER_GID} -m ${USERNAME} \
    && apt-get update \
    && apt-get install -y sudo \
    && echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/${USERNAME} \
    && chmod 0440 /etc/sudoers.d/${USERNAME} \
    && rm -rf /var/lib/apt/lists/*

# 将构建上下文复制进镜像，支持无需挂载直接运行
WORKDIR /testbed
COPY . /testbed
RUN chown -R ${USER_UID}:${USER_GID} /testbed

USER ${USERNAME}
WORKDIR /testbed
# 初始化 Git 仓库并生成一次基础提交，记录 base commit
RUN git init \
    && git config user.name "CSBench" \
    && git config user.email "csbench@example.local" \
    && git add -A \
    && git commit -m "Base commit" \
    && git rev-parse HEAD > .base_commit

# 默认进入交互式 shell
CMD ["bash"]
