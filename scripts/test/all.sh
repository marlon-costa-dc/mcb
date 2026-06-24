#!/usr/bin/env bash
# /// cosmos-command
# verb = "test"
# what = "all"
# domain = "quality"
# summary = "Run the workspace's default test gate"
# description = "Delegates to the existing 'make test' target in the main Makefile."
# example = "make test WHAT=all"
# mutates = false
# ///
set -euo pipefail
exec make test
