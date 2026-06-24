#!/usr/bin/env bash
# /// cosmos-command
# verb = "clean"
# what = "all"
# domain = "workspace"
# summary = "Run the workspace's default clean target"
# description = "Delegates to the existing 'make clean' target in the main Makefile."
# example = "make clean WHAT=all APPLY=Y"
# mutates = true
# params = [
#   { name = "APPLY", help = "Confirm destructive operation", required = true, choices = ["Y"] }
# ]
# ///
set -euo pipefail
exec make clean
