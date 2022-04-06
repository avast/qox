#!/usr/bin/env bash
# CHANGEDIR: ROOT
# HELP: run tests
set -e

source .venv/bin/activate

set -x
pytest -l tests
