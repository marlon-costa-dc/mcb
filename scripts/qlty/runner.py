"""Qlty Runner.

Copyright (c) 2025 MCB Contributors. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import subprocess  # nosec B404
import sys
from pathlib import Path

from qlty.model import SarifIssue
from qlty.parser import parse_sarif_file


def run_qlty_check(
    output_file: Path = Path("qlty.check.current.sarif"),
) -> list[SarifIssue]:
    """Run qlty check --all --sarif, save to file, and parse SARIF output."""
    print("🔄 Running qlty check --all --sarif...")

    try:
        result = subprocess.run(  # nosec B603 B607
            ["qlty", "check", "--all", "--sarif"],
            capture_output=True,
            text=True,
            timeout=300,
            check=False,
        )

        if not result.stdout.strip():
            print("   ✅ No issues found (clean)")
            return []

        output_file.write_text(result.stdout, encoding="utf-8")
        print(f"   💾 Saved SARIF to {output_file}")

        issues = parse_sarif_file(output_file)
        print(f"   📊 Found {len(issues)} issues")
        return issues

    except subprocess.TimeoutExpired:
        print("   ❌ qlty check timed out after 300s", file=sys.stderr)
        return []
    except (OSError, subprocess.SubprocessError) as e:
        print(f"   ❌ Error running qlty: {e}", file=sys.stderr)
        return []


def run_qlty_smells(
    output_file: Path = Path("qlty.smells.sarif"),
) -> list[SarifIssue]:
    """Run qlty smells --all --sarif, save to file, and parse SARIF output."""
    print("🔄 Running qlty smells --all --sarif...")

    try:
        result = subprocess.run(  # nosec B603 B607
            ["qlty", "smells", "--all", "--sarif"],
            capture_output=True,
            text=True,
            timeout=300,
            check=False,
        )

        if not result.stdout.strip():
            print("   ✅ No smells found (clean)")
            return []

        output_file.write_text(result.stdout, encoding="utf-8")
        print(f"   💾 Saved SARIF to {output_file}")

        issues = parse_sarif_file(output_file)
        # Mark issues as 'smell' category if not present
        for issue in issues:
            if not issue.category:
                issue.category = "smell"

        print(f"   📊 Found {len(issues)} smells")
        return issues

    except subprocess.TimeoutExpired:
        print("   ❌ qlty smells timed out after 300s", file=sys.stderr)
        return []
    except (OSError, subprocess.SubprocessError) as e:
        print(f"   ❌ Error running qlty smells: {e}", file=sys.stderr)
        return []
