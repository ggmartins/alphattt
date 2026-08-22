#!/bin/bash

cd $(dirname "$(realpath "${BASH_SOURCE[0]}")")

uv run --with pydantic --with pytest --with pytest-cov pytest
