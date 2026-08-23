#!/usr/bin/env bash

cd $(dirname "$(realpath "${BASH_SOURCE[0]}")")

APP=my-app:v0

docker build -t $APP .

