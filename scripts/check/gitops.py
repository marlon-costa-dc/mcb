#!/usr/bin/env python3
"""Check Gitops.

Copyright (c) 2025 MCB Contributors. All rights reserved.
SPDX-License-Identifier: MIT
"""
# /// cosmos-command
# verb = "check"
# what = "gitops"
# domain = "quality"
# summary = "Validate GitOps manifests through the shared qlty-style pipeline"
# description = "Discovers Helm/Kustomize targets under k8s/ and reports SKIP when the tree has no manifests yet."
# example = "make check WHAT=gitops"
# mutates = false
# ///
from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from lib.core import get_logger  # noqa: E402  # lib/ is only resolvable after sys.path injection above

logger = get_logger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run MCB GitOps validation discovery.")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
        help="Workspace root. Defaults to the repository root.",
    )
    return parser.parse_args()


def main() -> int:
    from lib.gitops import summarize

    args = parse_args()
    k8s_root = args.root / "k8s"
    summary = summarize(k8s_root)
    logger.info(f"GITOPS {summary.status}: {summary.message}")
    if summary.report.total_issues:
        logger.info(summary.report.generate_summary())
    for target in summary.targets:
        logger.info(f"{target.kind}\t{target.path}")
    return 0 if summary.status in {"OK", "SKIP"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
