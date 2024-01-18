# Constructs the environment within which we will build the grain pip wheels.
#
# From /tmp/grain,
# ❯ DOCKER_BUILDKIT=1 docker build \
#     --build-arg PYTHON_VERSION=${PYTHON_VERSION} \
#     -t grain:${PYTHON_VERSION} - < grain/oss/build.Dockerfile
# ❯ docker run --rm -it -v /tmp/grain:/tmp/grain \
#      grain:${PYTHON_VERSION} bash

FROM ubuntu:22.04
LABEL maintainer="Grain team <grain-dev@google.com>"

# Declare args after FROM because the args declared before FROM can't be used in
# any instructions after a FROM
ARG PYTHON_VERSION
ARG BAZEL_VERSION

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && apt install -y --no-install-recommends software-properties-common
RUN apt update && apt install -y --no-install-recommends \
        build-essential \
        curl \
        git \
        pkg-config \
        rename \
        rsync \
        unzip \
        vim \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Setup python
RUN apt-get update && apt-get install -y \
    python3-dev python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/* && \
    python${PYTHON_VERSION} -m pip install pip --upgrade && \
    update-alternatives --install /usr/bin/python python /usr/bin/python${PYTHON_VERSION} 0

# Install bazel
RUN curl -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36" -fSsL -o /usr/bin/bazel https://github.com/bazelbuild/bazelisk/releases/download/v1.17.0/bazelisk-linux-arm64 && \
    chmod a+x /usr/bin/bazel

# Install pip dependencies needed for grain
# NOTE(gspschmid): Constraints should go into quotes to be interpreted correctly?
# NOTE(gspschmid): Should require "array_record>=0.5.0", since earlier versions were erroneously
#   published as universal (arch-agnostic) wheels. Since this isn't available at the moment,
#   adding this constraint would break the build.
RUN --mount=type=cache,target=/root/.cache \
  python${PYTHON_VERSION} -m pip install -U \
    absl-py \
    array_record \
    build \
    cloudpickle \
    dm-tree \
    etils[epath] \
    more-itertools>=9.1.0 \
    numpy;

# Install pip dependencies needed for grain tests
RUN --mount=type=cache,target=/root/.cache \
  python${PYTHON_VERSION} -m pip install -U \
    dill \
    jax \
    jaxlib \
    tensorflow \
    tensorflow-datasets;

WORKDIR "/tmp/grain"