#!/usr/bin/env bash

cd $(dirname "$(realpath "${BASH_SOURCE[0]}")")

APP=my-app:v0

docker build -t $APP .
for node in $(docker ps --format '{{.Names}}' | grep '^desktop-'); do
  echo "Loading image into $node"
  docker save $APP | docker exec -i "$node" ctr -n k8s.io images import -
done
