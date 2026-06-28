"""Lib Tests Test Gitops.

Copyright (c) 2025 MCB Contributors. All rights reserved.
SPDX-License-Identifier: MIT
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


class GitOpsDiscoveryTests(unittest.TestCase):
    def test_readme_only_k8s_tree_is_clean_skip(self) -> None:
        from lib.gitops import summarize

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "k8s").mkdir()
            (root / "k8s" / "README.md").write_text("# placeholder\n", encoding="utf-8")

            summary = summarize(root / "k8s")

        self.assertEqual(summary.status, "SKIP")
        self.assertEqual(summary.targets, [])
        self.assertIn("no Helm or Kustomize targets", summary.message)

    def test_discovers_helm_and_kustomize_targets(self) -> None:
        from lib.gitops import discover_targets

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            chart = root / "k8s" / "chart"
            overlay = root / "k8s" / "overlay"
            chart.mkdir(parents=True)
            overlay.mkdir(parents=True)
            (chart / "Chart.yaml").write_text("apiVersion: v2\nname: sample\n", encoding="utf-8")
            (overlay / "kustomization.yaml").write_text("resources: []\n", encoding="utf-8")

            targets = discover_targets(root / "k8s")

        self.assertEqual(
            [(target.kind, target.path.name) for target in targets], [("helm", "chart"), ("kustomize", "overlay")]
        )

    def test_policy_issues_reuse_qlty_report_model(self) -> None:
        from lib.gitops import analyze

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workload = root / "k8s" / "workload.yaml"
            workload.parent.mkdir(parents=True)
            workload.write_text(
                "\n".join(
                    [
                        "apiVersion: apps/v1",
                        "kind: Deployment",
                        "metadata:",
                        "  name: sample",
                        "spec:",
                        "  template:",
                        "    spec:",
                        "      containers:",
                        "        - name: app",
                        "          image: nginx:latest",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            report = analyze(root / "k8s")

        self.assertEqual(report.total_issues, 1)
        self.assertEqual(report.issues[0].rule_id, "gitops:no-latest-image")
        self.assertEqual(report.by_category["gitops"], 1)

    def test_policy_issue_line_points_to_image_key_not_first_matching_value(self) -> None:
        from lib.gitops import analyze

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workload = root / "k8s" / "workload.yaml"
            workload.parent.mkdir(parents=True)
            workload.write_text(
                "\n".join(
                    [
                        "apiVersion: v1",
                        "kind: Pod",
                        "metadata:",
                        "  name: latest",
                        "  annotations:",
                        "    copied-image: busybox:latest",
                        "spec:",
                        "  containers:",
                        "    - name: app",
                        "      image: busybox:latest",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            report = analyze(root / "k8s")

        self.assertEqual(report.total_issues, 1)
        self.assertEqual(report.issues[0].start_line, 10)


class GitOpsCommandTests(unittest.TestCase):
    def test_command_skips_without_using_cluster_clis(self) -> None:
        command = SCRIPTS / "check" / "gitops.py"

        result = subprocess.run(
            [sys.executable, str(command), "--root", str(SCRIPTS.parents[0])],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("GITOPS SKIP", result.stdout)
        combined = result.stdout + result.stderr
        self.assertNotIn("kubectl", combined)
        self.assertNotIn("vault ", combined)
        self.assertNotIn("argocd ", combined)

    def test_command_fails_on_latest_image_policy_issue(self) -> None:
        command = SCRIPTS / "check" / "gitops.py"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = root / "k8s" / "pod.yaml"
            manifest.parent.mkdir(parents=True)
            manifest.write_text(
                "apiVersion: v1\nkind: Pod\nmetadata:\n  name: latest\nspec:\n  containers:\n    - name: app\n      image: busybox:latest\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, str(command), "--root", str(root)],
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("gitops:no-latest-image", result.stdout)


if __name__ == "__main__":
    unittest.main()
