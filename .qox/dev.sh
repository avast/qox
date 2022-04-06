#!/usr/bin/env bash
# CHANGEDIR: ROOT
# HELP: ensure dev environment is in good shape
# HELP: always create a fresh venv
set -xe

rm -rf .venv
python3.10 -m venv .venv
.venv/bin/pip install --editable ".[lint,test]"
