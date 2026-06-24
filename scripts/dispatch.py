"""Thin entrypoint for the workspace command framework.

Copied into <workspace>/scripts/dispatch.py by ~/.ai-hub distribution.
"""

from __future__ import annotations

from lib.cosmos_command import main

if __name__ == "__main__":
    raise SystemExit(main())
