#!/usr/bin/env bash
# /// cosmos-command
# verb = "ship"
# what = "all"
# domain = "release"
# summary = "Run the workspace's default ship/release target"
# description = "Delegates to the existing 'make ship' target in the main Makefile."
# example = "make ship WHAT=all APPLY=Y"
# mutates = true
# params = [
#   { name = "APPLY", help = "Confirm release operation", required = true, choices = ["Y"] }
# ]
# ///
set -euo pipefail
exec make ship
