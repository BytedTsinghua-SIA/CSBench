FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive \
    TZ=Etc/UTC

# 更换 apt 源为国内镜像

# 基础工具链与调试工具（x86_64）
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       gcc \
       gdb \
       binutils \
       make \
       python3 \
       python3-dev \
       python3-pip \
       file \
       git \
       curl \
       ca-certificates \
       vim \
       less \
    && rm -rf /var/lib/apt/lists/*

# 安装 Node.js + npm
ENV NODE_VERSION=24.11.0
ENV NODE_DISTRO=node-v${NODE_VERSION}-linux-x64
ENV NODE_DIR=/usr/local/lib/nodejs/${NODE_DISTRO}
RUN mkdir -p /usr/local/lib/nodejs \
    && curl -fsSL https://nodejs.org/dist/v${NODE_VERSION}/${NODE_DISTRO}.tar.xz -o /tmp/${NODE_DISTRO}.tar.xz \
    && tar -xJf /tmp/${NODE_DISTRO}.tar.xz -C /usr/local/lib/nodejs \
    && rm /tmp/${NODE_DISTRO}.tar.xz \
    && ln -sf ${NODE_DIR}/bin/node /usr/local/bin/node \
    && ln -sf ${NODE_DIR}/bin/npm /usr/local/bin/npm \
    && ln -sf ${NODE_DIR}/bin/npx /usr/local/bin/npx \
    && chmod -R a+rx /usr/local/lib/nodejs/${NODE_DISTRO}
ENV PATH="${NODE_DIR}/bin:${PATH}"

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
RUN pip3 install --no-cache-dir pytest pycosat

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


