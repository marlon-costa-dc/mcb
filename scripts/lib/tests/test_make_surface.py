from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MAKEFILE = ROOT / "Makefile"
DISPATCH = ROOT / "makefiles" / "dispatch.mk"


class MakeSurfaceContractTests(unittest.TestCase):
    def test_help_does_not_imply_apply_for_read_only_checks(self) -> None:
        help_source = MAKEFILE.read_text(encoding="utf-8")

        self.assertNotIn("check WHAT=guard | WHAT=ci | WHAT=optimize [APPLY=Y]", help_source)
        self.assertIn("check WHAT=guard | WHAT=ci", help_source)
        self.assertIn("check WHAT=optimize [APPLY=Y]", help_source)
        self.assertIn("check WHAT=fix     ACT=%s [APPLY=Y]", help_source)

    def test_mutating_make_arms_are_apply_gated(self) -> None:
        dispatch = DISPATCH.read_text(encoding="utf-8")

        gated_markers = {
            "ship add": "$(call gate,stage files",
            "ship commit before add": "$(call gate,commit",
            "ship pull": "$(call gate,pull",
            "ship branch create": "$(call gate,create branch",
            "ship checkout": "$(call gate,checkout",
            "ship tag": "$(call gate,tag",
            "ship stash": "$(call gate,stash",
            "ship stash-pop": "$(call gate,stash pop",
            "ship unstage": "$(call gate,unstage",
            "pr rerun": "$(call gate,rerun",
            "sub sync": "$(call gate,sync submodules",
            "sub propagate": "$(call gate,stage submodule",
            "release package": "$(call gate,package release",
            "fix fmt": "$(call gate,auto-fix fmt",
            "fix lint": "$(call gate,auto-fix lint",
            "fix docs": "$(call gate,auto-fix docs",
            "dev run": "$(call gate,start dev server",
            "dev docker-up": "$(call gate,start Docker test services",
            "dev docker-down": "$(call gate,stop Docker test services",
            "dev docker-logs": "$(call gate,follow Docker logs",
            "dev docker-test": "$(call gate,run Docker test services",
        }

        for label, marker in gated_markers.items():
            with self.subTest(label=label):
                self.assertIn(marker, dispatch)

        version_bump = dispatch.split("define MCB_VERSION_BUMP", 1)[1].split("endef", 1)[0]
        self.assertIn("$(call gate,version bump", version_bump)

    def test_docs_fix_and_e2e_have_explicit_gates(self) -> None:
        dispatch = DISPATCH.read_text(encoding="utf-8")

        self.assertIn('if [ "$(FIX)" = "1" ]; then $(call gate,fix markdown docs);', dispatch)
        self.assertIn("define MCB_E2E\n$(call gate,run Playwright E2E", dispatch)

    def test_invalid_nested_choices_fail_before_dry_run_gates(self) -> None:
        commands = [
            ["make", "build", "WHAT=codegen", "ACT=__invalid__"],
            ["make", "check", "WHAT=fix", "ACT=__invalid__"],
            ["make", "check", "WHAT=dev", "ACT=__invalid__"],
            ["make", "ship", "WHAT=release", "ACT=__invalid__"],
            ["make", "ship", "WHAT=pr", "ACT=__invalid__"],
            ["make", "ship", "WHAT=sub", "ACT=__invalid__"],
            ["make", "clean", "WHAT=__invalid__"],
        ]

        for command in commands:
            with self.subTest(command=" ".join(command)):
                result = subprocess.run(command, cwd=ROOT, check=False, capture_output=True, text=True)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertIn("ERRO:", result.stdout + result.stderr)

    def test_surface_command_runs_safe_matrix(self) -> None:
        command = ROOT / "scripts" / "check" / "surface.py"

        result = subprocess.run([sys.executable, str(command)], cwd=ROOT, check=False, capture_output=True, text=True)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("SURFACE OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
