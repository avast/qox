#!/usr/bin/env bash
# CHANGEDIR: ROOT
# HELP: run all quality tools, crash early
set -xe

qox fmt
qox types
qox test
