#!/bin/bash
# This script copies grain from internal repo, builds a docker, and
# builds pip wheels for all Python versions.

set -e -x

export TMP_FOLDER="/tmp/grain"

# Clean previous folders/images.
[ -f $TMP_FOLDER ] && rm -rf $TMP_FOLDER

export PYTHON_VERSION="3.10"

 # Using a previous version of Blaze to avoid:
 # https://github.com/bazelbuild/bazel/issues/8622
export BAZEL_VERSION="5.4.0"

docker rmi -f grain:${PYTHON_VERSION}
docker rm -f grain

# Copies repo contents to temporary folder (analogous to copybara step, but nothing to export).
cp -r ./ $TMP_FOLDER

pushd $TMP_FOLDER
DOCKER_BUILDKIT=1 docker build --progress=plain --no-cache \
  --build-arg PYTHON_VERSION=${PYTHON_VERSION} \
  --build-arg BAZEL_VERSION=${BAZEL_VERSION} \
  -t grain:${PYTHON_VERSION} - < grain/oss/build.Dockerfile

docker run --rm -a stdin -a stdout -a stderr \
  --env PYTHON_VERSION=${PYTHON_VERSION} \
  --env BAZEL_VERSION=${BAZEL_VERSION} \
  -v $TMP_FOLDER:/tmp/grain \
  --name grain grain:${PYTHON_VERSION} \
  bash grain/oss/build_whl.sh
popd

ls $TMP_FOLDER/all_dist/*.whl