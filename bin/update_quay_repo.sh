#!/usr/bin/env bash
set -e
# build the image and retrieve the image id, this should work regardless of other running containers
export IMAGE_VERSION="${1:-1.0.1}"
rm -f Rules_Engine.properties

export IMAGE_NAME=image_to_be_pushed
export CONTAINER_ID

docker build -t "${IMAGE_NAME}" .

docker run "${IMAGE_NAME}"
CONTAINER_ID=$(docker ps -l | awk -v val="${IMAGE_NAME}" '$2 == val {print $1}')
echo "${CONTAINER_ID}"

# commit and push the image to quay container registry
docker commit "${CONTAINER_ID}" registry-dev.cigna.com/maa-dataops-rules-engine/maa-dataops-rules-engine-build:${IMAGE_VERSION}
docker push registry-dev.cigna.com/maa-dataops-rules-engine/maa-dataops-rules-engine-build:${IMAGE_VERSION}

if [ "$(docker ps -q -f name="${IMAGE_NAME}")" ]; then
  docker kill "${CONTAINER_ID}"
fi

docker rm "${CONTAINER_ID}"

docker pull registry-dev.cigna.com/maa-dataops-rules-engine/maa-dataops-rules-engine-build:${IMAGE_VERSION}
./bin/run_docker.sh rules_engine
