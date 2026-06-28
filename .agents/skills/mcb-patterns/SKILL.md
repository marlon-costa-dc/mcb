---
name: mcb-patterns
description: Central index and quick reference for MCB project patterns. Use when starting work in the MCB Rust workspace; delegates to domain-specific skills for details.
license: MIT
metadata:
  version: 1.0.0
---

# MCB Project Patterns — Quick Reference

**UTILITY SKILL**

Central index for the MCB (Memory Context Browser) Rust workspace. Use this skill to find the right domain-specific skill, then follow it.

**Version:** `0.3.2`  
**Stack:** Rust 2024, MSRV `1.92`, 7-crate workspace, Loco.rs/SeaQL baseline.  
**Sources of truth:** `Cargo.toml`, `Makefile`, `scripts/lib/mcb.sh`, `AGENTS.md`, `docs/architecture/PATTERNS.md`.

## Domain-specific skills

| Topic | Skill | When to use |
|-------|-------|-------------|
| Make verbs | `mcb-make-verbs` | Build, test, lint, validate, ship, bootstrap |
| Architecture layers | `mcb-architecture-layers` | Crate boundaries, imports, adding modules |
| Error handling | `mcb-error-handling` | `Result<T>`, `?`, `tracing`, no unwrap/panic |
| Import rules | `mcb-import-rules` | Import order, visibility, re-exports |
| Testing | `mcb-testing-patterns` | TDD, test layout, rstest/mockall/insta |
| Quality gates | `mcb-quality-gates` | Validation sequence before commit |

## Architecture in 30s

```text
mcb                 # CLI facade binary
  -> mcb-server     # MCP protocol, Axum HTTP, handlers, admin UI
    -> mcb-infrastructure  # DI/linkme + AppContext, Loco config, cache, logging
      -> mcb-domain        # entities, value objects, port traits, errors
  -> mcb-providers   # adapters for embedding, vector store, DB, git, parsers
  -> mcb-validate    # architecture rule engine
  -> mcb-utils       # shared leaf utilities
```

Dependency direction is one-way inward: `mcb-server → mcb-infrastructure → mcb-providers → mcb-domain`.

## Daily commands

```bash
make build                    # debug build
make test SCOPE=unit          # unit tests
make check WHAT=lint          # fmt + clippy
make check WHAT=validate QUICK=1  # architecture rules
make check WHAT=guard         # banned-pattern scan
```

## Good practices checklist

- [ ] No `unwrap`/`expect`/`panic`/`todo` outside tests — use `?`
- [ ] Construct errors via `Error::<variant>("...")` factory methods
- [ ] Import order: `std` → external → `mcb_*` → `crate::`
- [ ] Use domain ports in handlers; never concrete providers
- [ ] Tests in `tests/` directory, not inline
- [ ] Run `make check WHAT=guard` before committing

## Bad practices (auto-fail)

| Don't | Why |
|-------|-----|
| `unwrap()` in prod code | Hides failure paths |
| Bypass `make`/`mcb.sh` | Breaks monopoly and gates |
| Edit `.beads/*.jsonl` by hand | Corrupts Dolt graph |
| Port traits outside `mcb-domain` | Violates Clean Architecture |
| Raw `String`/`Uuid` as domain IDs | Use `define_id!` |
| `println!` in prod code | Use `tracing` |
| `TODO`/`FIXME` in committed code | Stubs forbidden |

## Beads workflow

```bash
bd prime                   # load context
bd ready                   # list actionable items
bd update <id> --claim     # take ownership before editing
bd close <id> --reason "make check WHAT=lint passed"
```

## Verification before committing

```bash
make check WHAT=lint && make test SCOPE=unit && make check WHAT=validate QUICK=1 && make check WHAT=guard
```

## References

- `AGENTS.md` — full project agent rules
- `Makefile` — canonical command SSOT
- `scripts/lib/mcb.sh` — monopoly script
- `docs/architecture/PATTERNS.md` — detailed patterns
- `docs/developer/CONTRIBUTING.md` — contribution guide
- `docs/MCP_TOOLS.md` — public MCP tool contract
