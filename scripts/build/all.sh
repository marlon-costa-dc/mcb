#!/usr/bin/env bash
# /// cosmos-command
# verb = "build"
# what = "all"
# domain = "build"
# summary = "Run the workspace's default build target"
# description = "Delegates to the existing 'make build' target in the main Makefile."
# example = "make build WHAT=all"
# mutates = false
# ///
set -euo pipefail
exec make build
