"""GitOps validation helpers built on the existing script framework.

This module is intentionally small: it discovers render targets once and returns
structured summaries that the qlty reporting/fix layers can consume later.
Online Kubernetes, Vault, and ArgoCD checks must be added through library
clients here, not through kubectl/vault/argocd shell commands.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

KUSTOMIZE_FILES = frozenset(
    {
        "kustomization.yaml",
        "kustomization.yml",
        "Kustomization",
    }
)


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
    if not targets:
        return GitOpsSummary(
            status="SKIP",
            message=f"{root}: no Helm or Kustomize targets found",
            targets=[],
        )
    return GitOpsSummary(
        status="OK",
        message=f"{root}: discovered {len(targets)} GitOps target(s)",
        targets=targets,
    )
