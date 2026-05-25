# Use Python official image as base image
FROM python:3.11-slim

# Install system dependencies and build tools
RUN apt-get update \
    && apt-get install -y \
    git \
    wget \
    curl \
    build-essential \
    cmake \
    pkg-config \
    libssl-dev \
    ninja-build \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir --upgrade pip setuptools wheel
RUN pip3 install --no-cache-dir torch==2.1.0 --index-url https://download.pytorch.org/whl/cpu

RUN pip3 install --no-cache-dir \
    sentencepiece \
    protobuf \
    datasets \
    huggingface_hub \
    hf_transfer \
    accelerate \
    peft \
    trl

RUN pip3 install --no-cache-dir "transformers>=4.40.0,<5.0.0"

RUN pip3 install --no-cache-dir unsloth unsloth-zoo

RUN (pip3 install --no-cache-dir bitsandbytes || echo "Note: bitsandbytes skipped") || true
RUN (pip3 install --no-cache-dir xformers || echo "Note: xformers skipped") || true
RUN (pip3 install --no-cache-dir triton || echo "Note: triton skipped") || true
RUN (pip3 install --no-cache-dir cut_cross_entropy || echo "Note: cut_cross_entropy skipped") || true

# Create non-root user for easier compilation and debugging in container
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

# Install pytest for testing
RUN pip3 install --no-cache-dir pytest

# Copy build context into image, supports running without mounting
WORKDIR /testbed
COPY . /testbed
RUN chown -R ${USER_UID}:${USER_GID} /testbed

USER ${USERNAME}
WORKDIR /testbed
# Initialize Git repository and create a base commit, record base commit
RUN git init \
    && git config user.name "CSBench" \
    && git config user.email "csbench@example.local" \
    && git add -A \
    && git commit -m "Base commit" \
    && git rev-parse HEAD > .base_commit

# Default to interactive shell
CMD ["bash"]
