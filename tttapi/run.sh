#!/bin/bash

cd $(dirname "$(realpath "${BASH_SOURCE[0]}")")

cd src; ./app.py --port 8081
