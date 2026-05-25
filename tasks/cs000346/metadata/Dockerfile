# Use Ubuntu as base image for C++ development
FROM ubuntu:20.04

# Set environment variables to avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    g++ \
    clang \
    cmake \
    git \
    python3 \
    python3-pip \
    python3-dev \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages for testing
RUN pip3 install --no-cache-dir \
    numpy \
    pytest \
    pytest-cov

# Install additional development tools
RUN apt-get update && apt-get install -y \
    vim \
    gdb \
    valgrind \
    && rm -rf /var/lib/apt/lists/*

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

# 为测试安装 pytest
RUN pip3 install --no-cache-dir pytest

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
