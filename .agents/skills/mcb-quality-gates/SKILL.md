---
name: mcb-quality-gates
description: Quality gate sequence and interpretation for the MCB Rust workspace. Use when validating changes before commit or debugging gate failures.
license: MIT
metadata:
  version: 1.0.0
---

# MCB Quality Gates

**UTILITY SKILL**

Mandatory validation sequence for the MCB Rust workspace.

## USE FOR

- Validating changes before commit.
- Interpreting gate failures.

## DO NOT USE FOR

- Questions unrelated to MCB quality gates.
- Generic CI/CD outside MCB.

## Critical rules

- Run gates in order of speed: format → lint → unit tests → integration tests → architecture validation → guard.
- A red gate is a blocker; fix the root cause before proceeding.
- Keep failure evidence in beads: command, output, exit code.

## Gate sequence

```bash
# 1. Fast feedback
make check WHAT=fix ACT=fmt APPLY=Y   # auto-format
make check WHAT=lint                   # fmt check + clippy --all-targets -D warnings

# 2. Behavior
make test SCOPE=unit                   # unit tests
make test SCOPE=integration            # integration tests

# 3. Architecture and banned patterns
make check WHAT=validate QUICK=1       # architecture rules
make check WHAT=guard                  # unwrap/panic/todo/TODO/#[allow] scan

# 4. Full CI
make check WHAT=ci                     # everything CI runs
```

## Gate definitions

| Gate | Tool / Command | Failure means |
|------|----------------|---------------|
| Format | `cargo fmt --all -- --check` | Code is not rustfmt-clean |
| Lint | `cargo clippy --all-targets -- -D warnings` | Clippy warning or error |
| Unit tests | `cargo test --workspace --test unit` / nextest | Unit test failed |
| Integration tests | `cargo test --workspace --test '*integration*'` | Integration test failed |
| Architecture | `make check WHAT=validate` | Dependency rule or crate boundary violated |
| Guard | `make check WHAT=guard` | Banned pattern introduced |
| Audit | `make check WHAT=audit` | Security advisory or license issue |

## Pre-commit hook

`make boot WHAT=hooks` installs:

```bash
guard --staged
cargo fmt --all -- --check
cargo clippy --workspace -- -D warnings
typos
unit tests
```

## Pre-push hook

```bash
cargo fmt --all -- --check
cargo clippy --all-targets -- -D warnings
make test
make test SCOPE=doc
make check WHAT=validate QUICK=1
```

## Docs-only changes

```bash
make build WHAT=docs ACT=lint
make build WHAT=docs ACT=validate QUICK=1
```

## Good example

```bash
make check WHAT=lint && make test SCOPE=unit && make check WHAT=validate QUICK=1 && make check WHAT=guard
```

## Bad example

```bash
# WRONG: skipping lint and running only tests
cargo test
```

## Verification

```bash
make check WHAT=ci
```

## References

- `Makefile` — gate definitions.
- `scripts/lib/mcb.sh` — guard implementation.
- `AGENTS.md` — verification expectations.
