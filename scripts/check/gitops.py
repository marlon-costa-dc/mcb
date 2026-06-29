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

import sys
from pathlib import Path

import typer
from pydantic import BaseModel

SCRIPTS = Path(__file__).resolve().parents[1]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from lib.cli import create_app_with_common_params, register_result_command  # noqa: E402
from lib.core import get_logger, r  # noqa: E402
from lib.gitops import GitOpsSummary, summarize  # noqa: E402

logger = get_logger(__name__)


class GitopsParams(BaseModel):
    root: Path = Path(__file__).resolve().parents[2]


def run(params: GitopsParams) -> r[GitOpsSummary]:
    """Discover and validate GitOps manifests."""
    k8s_root = params.root / "k8s"
    summary = summarize(k8s_root)
    logger.info(f"GITOPS {summary.status}: {summary.message}")
    if summary.report.total_issues:
        logger.info(summary.report.generate_summary())
    for target in summary.targets:
        logger.info(f"{target.kind}\t{target.path}")
    if summary.status not in {"OK", "SKIP"}:
        return r[GitOpsSummary].fail(summary.message)
    return r[GitOpsSummary].ok(summary)


def main() -> None:
    app = create_app_with_common_params(
        name="check-gitops",
        help_text="Run MCB GitOps validation discovery.",
    )
    register_result_command(
        app,
        name="run",
        help_text="Discover and validate GitOps manifests.",
        model_cls=GitopsParams,
        handler=run,
    )
    typer.main.get_command(app)()


if __name__ == "__main__":
    main()
