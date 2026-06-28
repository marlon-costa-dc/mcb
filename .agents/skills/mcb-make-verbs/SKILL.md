---
name: mcb-make-verbs
description: Quick reference for the canonical MCB make verbs. Use when you need to build, test, lint, validate, ship, or bootstrap the MCB Rust workspace.
license: MIT
metadata:
  version: 1.0.0
---

# MCB Make Verbs

**UTILITY SKILL**

Canonical `make` interface for the MCB Rust workspace. Never call `cargo`/`git` directly.

## USE FOR

- Running builds, tests, lints, validations, docs, or git operations.
- Discovering the correct verb/phase for a task.

## DO NOT USE FOR

- Questions unrelated to MCB tooling.
- Creating projects from scratch.

## Critical rules

- Pattern: `make <verb> [WHAT=phase] [ACT=sub] [SCOPE=...] [APPLY=Y]`.
- Destructive verbs (`commit`, `push`, `clean`, `codegen`, `release`) are **DRY-RUN** unless `APPLY=Y`.
- Use `make help` for the live list.

## Daily verbs

| Task | Command |
|------|---------|
| Build workspace (debug) | `make build` |
| Release build | `make build RELEASE=1` |
| Run all tests | `make test` |
| Run unit tests | `make test SCOPE=unit` |
| Lint + format check | `make check WHAT=lint` |
| Auto-format code | `make check WHAT=fix ACT=fmt APPLY=Y` |
| Architecture validation | `make check WHAT=validate QUICK=1` |
| Banned-pattern scan | `make check WHAT=guard` |
| Full CI gate | `make check WHAT=ci` |
| Security advisory scan | `make check WHAT=audit` |
| Generate docs | `make build WHAT=docs` |
| Lint markdown | `make build WHAT=docs ACT=lint` |
| Validate docs/links | `make build WHAT=docs ACT=validate QUICK=1` |
| Git status | `make ship WHAT=status` |
| Commit (destructive) | `make ship WHAT=commit MSG='...' APPLY=Y` |
| Push (destructive) | `make ship WHAT=push APPLY=Y` |
| Bootstrap hooks/tools | `make boot` |
| Clean artifacts (destructive) | `make clean WHAT=build APPLY=Y` |

## Parameters

- `WHAT` — phase under the verb (e.g. `lint`, `validate`, `docs`).
- `ACT` — nested action under `WHAT` (e.g. `ACT=fmt` under `WHAT=fix`).
- `SCOPE` — test scope (`unit`, `integration`, `doc`, `e2e`, `all`).
- `APPLY=Y` — execute destructive verbs for real.
- `QUICK=1` — skip expensive checks (external link checks, full validation).
- `FIX=1` — auto-fix when available (markdownlint, rustfmt).
- `RELEASE=1` — release build.

## Examples

```bash
# Full local validation before a commit
make check WHAT=lint && make test SCOPE=unit && make check WHAT=validate QUICK=1

# Docs-only change
make build WHAT=docs ACT=lint
make build WHAT=docs ACT=validate QUICK=1

# Commit and push verified work
make ship WHAT=commit MSG='feat(mcb-server): add handler' APPLY=Y
make ship WHAT=push APPLY=Y
```

## Verification

```bash
make help
```

## References

- `Makefile` — SSOT for verbs and phases.
- `makefiles/dispatch.mk` — dispatch implementation.
- `scripts/lib/mcb.sh` — monopoly script backing the verbs.
