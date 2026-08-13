"""Lib Tests Test Make Surface.

Copyright (c) 2025 MCB Contributors. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from ._utilities.matchers import tm

ROOT = Path(__file__).resolve().parents[3]


def _run_make(*args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    for name in ("MAKEFLAGS", "MFLAGS", "MAKELEVEL"):
        env.pop(name, None)
    return subprocess.run(
        ["make", *args], cwd=ROOT, check=False, capture_output=True, text=True, env=env
    )


def test_help_lists_flext_public_verbs() -> None:
    result = _run_make("help", "WHAT=usage")
    combined = result.stdout + result.stderr

    tm.that(result.returncode == 0, combined)
    tm.that("work       WHAT=start|status|land|finish" in result.stdout)
    tm.that("_custom_run_mcb-hooks" in result.stdout)
    tm.that("golden" in result.stdout)


def test_custom_mutations_require_apply() -> None:
    # The public verbs are the contract a caller can invoke; the internal
    # `_serialized_*` targets are a generator implementation detail and were
    # removed when flext-infra dropped the `serialize-make` CLI route.
    commands = [
        ("fmt", "WHAT=apply", "APPLY=N"),
        ("fix", "WHAT=apply", "APPLY=N"),
        ("run", "WHAT=mcb-hooks", "APPLY=N"),
        ("gen", "WHAT=agent-pointers", "APPLY=N"),
    ]

    for command in commands:
        result = _run_make(*command)
        combined = result.stdout + result.stderr
        tm.that(
            result.returncode != 0,
            f"{command}: mutation ran without APPLY=Y\n{combined}",
        )
        tm.that(
            "requires APPLY=Y" in combined, f"{command}: missing APPLY gate\n{combined}"
        )


@pytest.mark.slow
@pytest.mark.timeout(900)
def test_invalid_nested_choices_fail_before_dry_run_gates() -> None:
    commands = [
        ["make", "build", "WHAT=codegen-__invalid__"],
        ["make", "check", "WHAT=fix-__invalid__"],
        ["make", "check", "WHAT=dev-__invalid__"],
        ["make", "release", "WHAT=__invalid__"],
        ["make", "work", "WHAT=pr-__invalid__"],
        ["make", "work", "WHAT=sub-__invalid__"],
        ["make", "clean", "WHAT=__invalid__"],
    ]

    for command in commands:
        result = subprocess.run(
            command, cwd=ROOT, check=False, capture_output=True, text=True
        )
        combined = result.stdout + result.stderr
        tm.that(
            result.returncode != 0,
            f"{' '.join(command)}: expected failure, got {result.returncode}\n{combined}",
        )
        tm.that(
            "ERROR:" in combined or "unsupported" in combined,
            f"{' '.join(command)}: missing flext error marker",
        )


@pytest.mark.slow
@pytest.mark.timeout(900)
def test_surface_command_runs_safe_matrix() -> None:
    command = ROOT / "scripts" / "check" / "surface.py"

    result = subprocess.run(
        [sys.executable, str(command)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    tm.that(result.returncode == 0, result.stdout + result.stderr)
    tm.that("SURFACE OK" in result.stdout)


def _hook_commands(hook_what: str) -> list[str]:
    """Return the commands make would execute for a hook handler.

    Expands the private handler directly through make's own dry-run, so the
    assertion reflects what the hook really runs rather than a copy of the
    Makefile text. The public `run` verb is skipped here because its dispatch
    wrapper is generator-owned plumbing, not part of the hook's gate contract.
    """
    result = _run_make("--dry-run", f"_custom_run_{hook_what}")
    recipe = result.stdout + result.stderr
    return [
        line.strip()
        for line in recipe.splitlines()
        if line.strip() and not line.lstrip().startswith("make[")
    ]


def test_pre_commit_hook_runs_under_ci_yes() -> None:
    """pre-commit must execute its gates with the CI=Y token.

    CI=Y is the ternary state that omits the gates CI workflows own
    (lint/format/pyrefly/markdown), which is what a fast commit gate wants.
    """
    commands = _hook_commands("mcb-hook-pre-commit")

    tm.that(bool(commands), "pre-commit handler expanded no commands")
    offenders = [line for line in commands if "CI=Y" not in line]
    tm.that(
        not offenders,
        "pre-commit commands missing CI=Y token:\n" + "\n".join(offenders),
    )


def test_pre_push_hook_runs_under_ci_no() -> None:
    """pre-push must execute its gates with the CI=N token.

    CI=N is the ternary state that runs the FULL suite with coverage and
    keeps every blocking gate, which is what a pre-push gate must do.
    """
    commands = _hook_commands("mcb-hook-pre-push")

    tm.that(bool(commands), "pre-push handler expanded no commands")
    offenders = [line for line in commands if "CI=N" not in line]
    tm.that(
        not offenders, "pre-push commands missing CI=N token:\n" + "\n".join(offenders)
    )


def test_generated_gitignore_keeps_declared_project_exceptions() -> None:
    """Regeneration must not drop the project's own ignore rules.

    `.gitignore` is a generated projection, so the project's rules live in the
    `extra_ignored_patterns` overlay of config/workspace.yaml (the mro-jnm1.3
    seam). Both sides are read from their real files here: if the overlay ever
    stops reaching the rendered artifact, the barrier that keeps machine
    config and tool output out of version control silently disappears.
    """
    manifest = yaml.safe_load((ROOT / "config" / "workspace.yaml").read_text())
    overlays = manifest.get("repository_policy_overlays") or []
    declared: list[str] = [
        pattern
        for overlay in overlays
        for pattern in (overlay.get("extra_ignored_patterns") or [])
    ]

    tm.that(
        bool(declared),
        "config/workspace.yaml declares no extra_ignored_patterns, so the"
        " project's ignore rules are not owned by the generator input",
    )

    rendered = {
        line.strip()
        for line in (ROOT / ".gitignore").read_text().splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }
    missing = [pattern for pattern in declared if pattern not in rendered]
    tm.that(
        not missing,
        "declared ignore patterns absent from the generated .gitignore:\n"
        + "\n".join(missing),
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
