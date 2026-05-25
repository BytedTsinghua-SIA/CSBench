FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive \
    TZ=Etc/UTC

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       gcc \
       gdb \
       binutils \
       make \
       python3 \
       python3-pip \
       file \
       git \
       curl \
       ca-certificates \
       vim \
       less \
       valgrind \
       maven \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /etc/gdb \
    && echo "set disassembly-flavor intel" > /etc/gdb/gdbinit

# Install OpenJDK 9 manually since it is not available in Ubuntu 22.04 repositories
RUN curl -fsSL https://download.java.net/java/GA/jdk9/9/binaries/openjdk-9_linux-x64_bin.tar.gz -o /tmp/openjdk9.tar.gz \
    && tar -xzf /tmp/openjdk9.tar.gz -C /opt \
    && rm /tmp/openjdk9.tar.gz \
    && update-alternatives --install /usr/bin/java java /opt/jdk-9/bin/java 1 \
    && update-alternatives --install /usr/bin/javac javac /opt/jdk-9/bin/javac 1

ENV JAVA_HOME=/opt/jdk-9
ENV PATH="${JAVA_HOME}/bin:${PATH}"

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

RUN pip3 install --no-cache-dir pytest

WORKDIR /testbed
COPY . /testbed
RUN chown -R ${USER_UID}:${USER_GID} /testbed

USER ${USERNAME}
WORKDIR /testbed
RUN git init \
    && git config user.name "CSBench" \
    && git config user.email "csbench@example.local" \
    && git add -A \
    && git commit -m "Base commit" \
    && git rev-parse HEAD > .base_commit

CMD ["bash"]
