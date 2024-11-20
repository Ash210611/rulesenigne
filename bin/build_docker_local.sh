#!/usr/bin/env bash
set -e

rm -f Rules_Engine.properties

export IMAGE_TAG="${1:-latest}"
export IMAGE_NAME=image_to_be_pushed
export CONTAINER_ID

docker build -t "${IMAGE_NAME}:${IMAGE_TAG}" .

docker run "${IMAGE_NAME}:${IMAGE_TAG}"
CONTAINER_ID=$(docker ps -l | awk -v val="${IMAGE_NAME}" '$2 == val {print $1}')
echo "${CONTAINER_ID}"

docker run -it --rm \
    --entrypoint="bash" \
     image_to_be_pushed