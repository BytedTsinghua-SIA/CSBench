FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install build dependencies
RUN set -eux && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        wget \
        build-essential \
        git \
        python3 \
        python3-pip \
        software-properties-common \
        apt-transport-https \
    && rm -rf /var/lib/apt/lists/*

# Install GCC 13 from PPA
RUN apt-get update && \
    apt-get install -y --no-install-recommends gnupg2 && \
    add-apt-repository -y ppa:ubuntu-toolchain-r/test && \
    apt-get update && \
    apt-get install -y --no-install-recommends gcc-13 g++-13 && \
    update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-13 100 && \
    update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-13 100 && \
    rm -rf /var/lib/apt/lists/*

# Install CMake 3.24.3 (support multi-arch)
RUN ARCH=$(uname -m) && \
    if [ "$ARCH" = "x86_64" ]; then CMAKE_ARCH="x86_64"; \
    elif [ "$ARCH" = "aarch64" ] || [ "$ARCH" = "arm64" ]; then CMAKE_ARCH="aarch64"; \
    else echo "Unsupported architecture: $ARCH" && exit 1; fi && \
    wget -q https://github.com/Kitware/CMake/releases/download/v3.24.3/cmake-3.24.3-linux-${CMAKE_ARCH}.sh -O /tmp/cmake.sh && \
    chmod +x /tmp/cmake.sh && \
    /tmp/cmake.sh --skip-license --prefix=/usr/local && \
    rm /tmp/cmake.sh && \
    ln -sf /usr/local/bin/cmake /usr/bin/cmake

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

