#!/usr/bin/env bash
# CHANGEDIR: ROOT
# HELP: run black
set -xe

black qox_pkg/qox.py tests
