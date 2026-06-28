#!/usr/bin/env python3
"""Analyze Qlty.

Copyright (c) 2025 MCB Contributors. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import sys

from qlty.main import main

if __name__ == "__main__":
    if "--markdown" in sys.argv:
        idx = sys.argv.index("--markdown")
        sys.argv[idx] = "--report-file"
    sys.exit(main())
