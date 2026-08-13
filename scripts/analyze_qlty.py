#!/usr/bin/env python3
"""Analyze Qlty.

Thin entrypoint that delegates to mcb_scripts.qlty.main.

Copyright (c) 2025 MCB Contributors. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from mcb_scripts.qlty.main import main

if __name__ == "__main__":
    main()
