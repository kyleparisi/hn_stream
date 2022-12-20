#!/usr/bin/env bash

set -e

black main.py "$@"
flake8 main.py
