#!/usr/bin/env bash
# CHANGEDIR: ROOT
# HELP: run linters
set -xe

black qox.py tests
mypy qox.py
