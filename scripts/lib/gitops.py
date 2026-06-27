"""GitOps validation helpers built on the existing script framework.

This module is intentionally small: it discovers render targets once and returns
structured summaries that the qlty reporting/fix layers can consume later.
Online Kubernetes, Vault, and ArgoCD checks must be added through library
clients here, not through kubectl/vault/argocd shell commands.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import cast

from qlty.model import SarifIssue, Severity
from qlty.report import AnalysisReport, analyze_issues
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq
from ruamel.yaml.error import YAMLError

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


@dataclass(frozen=True, slots=True)
class ImageReference:
    """Container image value with its YAML source line."""

    value: str
    line: int


YamlNode = CommentedMap | CommentedSeq | str | int | float | bool | None


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
        try:
            documents = _load_yaml_documents(path)
        except YAMLError as exc:
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
            for image in _image_references(document):
                if image.value.endswith(":latest"):
                    issues.append(
                        _issue(
                            "gitops:no-latest-image",
                            f"Container image must not use the mutable latest tag: {image.value}",
                            path,
                            image.line,
                        )
                    )
    return issues


def _yaml_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(path for path in root.rglob("*") if path.is_file() and path.suffix in YAML_SUFFIXES)


def _load_yaml_documents(path: Path) -> list[YamlNode]:
    parser = YAML(typ="rt")
    return cast("list[YamlNode]", list(parser.load_all(path)))


def _image_references(node: YamlNode) -> list[ImageReference]:
    references: list[ImageReference] = []
    if isinstance(node, CommentedMap):
        image = node.get("image")
        if isinstance(image, str):
            references.append(ImageReference(value=image, line=_line_for_key(node, "image")))
        for child in node.values():
            references.extend(_image_references(cast("YamlNode", child)))
    elif isinstance(node, CommentedSeq):
        for child in node:
            references.extend(_image_references(cast("YamlNode", child)))
    return references


def _line_for_key(node: CommentedMap, key: str) -> int:
    line, _column = cast("tuple[int, int]", node.lc.key(key))
    return line + 1


def _issue(rule_id: str, message: str, path: Path, line: int) -> SarifIssue:
    return SarifIssue(
        rule_id=rule_id,
        level=Severity.ERROR,
        message=message,
        file_path=str(path),
        start_line=line,
        category="gitops",
    )
