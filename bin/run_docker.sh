#!/usr/bin/env bash
set -e

export CONTAINER_NAME="${1}"
export IMAGE_URI="${2:-registry-dev.cigna.com/maa-dataops-rules-engine/maa-dataops-rules-engine-build}"
export CONTAINER_VERSION="${3:-latest}"

if [ -z "$1" ]
then
  echo "Container name is missing."
  exit
fi

if [ "$(docker ps -q -f name="${CONTAINER_NAME}")" ]; then
  docker exec -it "${CONTAINER_NAME}" bash
else
  docker run -it --rm \
    --entrypoint="bash" \
    --name ${CONTAINER_NAME} \
    "${IMAGE_URI}":"${CONTAINER_VERSION}"
fi

docker images

