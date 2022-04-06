#!/usr/bin/env bash
# CHANGEDIR: ROOT
# HELP: run tests
set -xe

PYTHONPATH=. .venv/bin/pytest -l tests
