#!/usr/bin/env bash
set -e


if [ -z "${LABEL}" ]; then
  echo "Label not set"
  exit 1
fi

IMAGE="ghcr.io/milesstoetzner/straussi3-subtenancy:${LABEL}"

docker build -t ${IMAGE} .
docker push ${IMAGE}
