#!/usr/bin/env bash
# CHANGEDIR: ROOT
# HELP: run linters
set -xe

black qox_pkg/qox.py tests
mypy qox_pkg/qox.py
