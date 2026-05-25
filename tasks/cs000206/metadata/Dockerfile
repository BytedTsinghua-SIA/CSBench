FROM ubuntu:22.04 AS builder

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    python3 \
    python3-pip \
    findutils \
    && rm -rf /var/lib/apt/lists/*


COPY . /tmp/buildsrc
RUN rm -rf /tmp/build /tmp/buildsrc/build \
    && cmake -S /tmp/buildsrc -B /tmp/build -DCMAKE_BUILD_TYPE=Release \
    && cmake --build /tmp/build -j"$(nproc)" \
    && mkdir -p /out \
    && ( find /tmp/buildsrc/bin -type f -name "*test_sim_scenes*" -executable | head -n 1 | xargs -I {} cp {} /out/test_sim_scenes ) \
    && chmod +x /out/test_sim_scenes \
    && rm -rf /tmp/build /tmp/buildsrc

FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    python3 \
    python3-pip \
    findutils \
    && rm -rf /var/lib/apt/lists/*

# 将构建阶段产物放入最终镜像，确保即使 test.sh 仅运行 pytest，也能找到可执行文件
COPY --from=builder /out/test_sim_scenes /testbed/bin/test_sim_scenes
RUN chmod +x /testbed/bin/test_sim_scenes

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
# 构建上下文是 src 目录，直接复制所有内容
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