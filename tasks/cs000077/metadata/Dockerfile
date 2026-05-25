FROM python:3.11-slim

# Install git early as requested and clean up apt caches.
RUN apt-get update \
    && apt-get install -y --no-install-recommends git build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install runtime dependencies for the assignment code.
RUN pip3 install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu \
    torch==2.1.2 \
    numpy==1.26.2 \
    tqdm==4.66.1

ARG USERNAME=student
ARG USER_UID=1000
ARG USER_GID=1000
RUN groupadd --gid ${USER_GID} ${USERNAME} && useradd --uid ${USER_UID} --gid ${USER_GID} -m ${USERNAME} && apt-get update && apt-get install -y sudo && echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/${USERNAME} && chmod 0440 /etc/sudoers.d/${USERNAME} && rm -rf /var/lib/apt/lists/*
RUN pip3 install --no-cache-dir pytest
WORKDIR /testbed
COPY . /testbed
RUN chown -R ${USER_UID}:${USER_GID} /testbed
USER ${USERNAME}
WORKDIR /testbed
RUN git init && git config user.name "CSBench" && git config user.email "csbench@example.local" && git add -A && git commit -m "Base commit" && git rev-parse HEAD > .base_commit
CMD ["bash"]
