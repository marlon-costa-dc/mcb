"""GitOps validation helpers built on the existing script framework.

This module is intentionally small: it discovers render targets once and returns
structured summaries that the qlty reporting/fix layers can consume later.
Online Kubernetes, Vault, and ArgoCD checks must be added through library
clients here, not through kubectl/vault/argocd shell commands.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from qlty.model import SarifIssue, Severity
from qlty.report import AnalysisReport, analyze_issues

KUSTOMIZE_FILES = frozenset(
    {
        "kustomization.yaml",
        "kustomization.yml",
        "Kustomization",
    }
)
YAML_SUFFIXES = frozenset({".yaml", ".yml"})


@dataclass(frozen=True, slots=True)
class GitOpsTarget:
    """A Helm or Kustomize render target."""

    kind: str
    path: Path


@dataclass(frozen=True, slots=True)
class GitOpsSummary:
    """Result of the lightweight GitOps discovery pass."""

    status: str
    message: str
    targets: list[GitOpsTarget]
    report: AnalysisReport


def discover_targets(root: Path) -> list[GitOpsTarget]:
    """Discover Helm and Kustomize render targets below ``root``."""

    if not root.exists():
        return []

    targets: list[GitOpsTarget] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path.name == "Chart.yaml":
            targets.append(GitOpsTarget(kind="helm", path=path.parent))
            continue
        if path.name in KUSTOMIZE_FILES:
            targets.append(GitOpsTarget(kind="kustomize", path=path.parent))

    seen: set[tuple[str, Path]] = set()
    unique: list[GitOpsTarget] = []
    for target in targets:
        key = (target.kind, target.path)
        if key in seen:
            continue
        seen.add(key)
        unique.append(target)
    return unique


def summarize(root: Path) -> GitOpsSummary:
    """Return a discovery summary for GitOps targets below ``root``."""

    targets = discover_targets(root)
    report = analyze(root)
    if report.total_issues:
        return GitOpsSummary(
            status="FAIL",
            message=f"{root}: {report.total_issues} GitOps policy issue(s)",
            targets=targets,
            report=report,
        )
    if not targets:
        return GitOpsSummary(
            status="SKIP",
            message=f"{root}: no Helm or Kustomize targets found",
            targets=[],
            report=report,
        )
    return GitOpsSummary(
        status="OK",
        message=f"{root}: discovered {len(targets)} GitOps target(s)",
        targets=targets,
        report=report,
    )


def analyze(root: Path) -> AnalysisReport:
    """Analyze GitOps source manifests through the existing qlty report model."""

    return analyze_issues(policy_issues(root))


def policy_issues(root: Path) -> list[SarifIssue]:
    """Return native GitOps policy issues discovered in source manifests."""

    issues: list[SarifIssue] = []
    for path in _yaml_files(root):
        text = path.read_text(encoding="utf-8")
        try:
            documents = list(yaml.safe_load_all(text))
        except yaml.YAMLError as exc:
            issues.append(
                _issue(
                    "gitops:yaml-parse",
                    f"YAML parse error: {exc}",
                    path,
                    1,
                )
            )
            continue
        for document in documents:
            if not isinstance(document, dict):
                continue
            for image in _images(document):
                if image.endswith(":latest"):
                    issues.append(
                        _issue(
                            "gitops:no-latest-image",
                            f"Container image must not use the mutable latest tag: {image}",
                            path,
                            _line_for(text, image),
                        )
                    )
    return issues


def _yaml_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(path for path in root.rglob("*") if path.is_file() and path.suffix in YAML_SUFFIXES)


def _images(value: Any) -> list[str]:
    images: list[str] = []
    if isinstance(value, dict):
        image = value.get("image")
        if isinstance(image, str):
            images.append(image)
        for child in value.values():
            images.extend(_images(child))
    elif isinstance(value, list):
        for child in value:
            images.extend(_images(child))
    return images


def _line_for(text: str, needle: str) -> int:
    for index, line in enumerate(text.splitlines(), start=1):
        if needle in line:
            return index
    return 1


def _issue(rule_id: str, message: str, path: Path, line: int) -> SarifIssue:
    return SarifIssue(
        rule_id=rule_id,
        level=Severity.ERROR,
        message=message,
        file_path=str(path),
        start_line=line,
        category="gitops",
    )
