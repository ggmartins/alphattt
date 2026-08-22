#!/bin/bash

cd $(dirname "$(realpath "${BASH_SOURCE[0]}")")

#docker run --rm -p 8000:8000 my-app:v0
#docker run --rm -p 3306:3306 mysql 
./build_docker.sh

docker compose up
