---
name: orchestrate
description: Use when executing any multi-step task in mcb with parallel/independent work — runs a coordinator↔executor loop coordinated by beads (bd) under a strict additive/reversible/validate-each-step safety doctrine to prevent regressions and file conflicts.
---

# Orchestrate (coordinator + executors via beads)

For substantial mcb work, run a **coordinator + specialized-executor** loop. The
coordinator (you, main loop) owns correctness; executors do scoped edits.

Before editing code, load **`mcb-patterns`** for the project-specific quick reference
(make verbs, architecture rules, good/bad practices, beads workflow).

> Canonical coordination rules of engagement (claim-before-edit, never-revert-others,
> no-pattern-deviation, breaking-glass, converge-fast, return-to-plan) live in
> **`CLAUDE.md › Multi-Agent Coordination Doctrine`** (SSOT). The doctrine below is the
> operational expression of those rules — it does not supersede them.

## Safety doctrine (inviolable)

1. **Additive** — add/adjust; never remove existing behavior without archiving to `.bak`.
2. **Reversible** — one atomic bead delivery per item; commit only when the current lane has explicit user authorization. Use `mv ... -> .bak`, never `rm`.
3. **Equivalence verified where claimed** — e.g. nextest test-count == `cargo test`; new dev profile must not change `release` or break `linkme` (`make test SCOPE=startup`).
4. **Validate-before-each-step** — run the matching gate (`make check WHAT=lint`, `make test`, `make check WHAT=validate`, or `make hook WHAT=pre-push`) with evidence before closing any item. No item closes red.
5. **No bypass** — `make`, `bd`, Edit, and `ast-grep` only; raw `git checkout`, `git restore`, `git reset`, `--ours`, `--theirs`, and manual state reconstruction are blocked by AGENTS.md. Commit/push only through `make git ... APPLY=Y` when the live user has authorized Git writes for the lane.
6. **Never hand-edit `.beads/*.jsonl`** — it is a generated export/interchange artifact, not the write surface. Use `bd context --json`, `bd dolt show --json`, `bd backup status --json`, and `bd status --json` to verify backend identity, connection mode, backup state, and issue counts; all bead create/update/close/dep/status/export/import changes go through the `bd` CLI only.
7. **MAXIMUM RULE — never idle-wait.** Never block waiting on an async/long action (CI, builds, deploys, remote jobs). Either *actively monitor* it (poll on a cadence) **or** switch to an independent non-blocking bead and return when the action completes. Idle waiting is forbidden; there is always either monitoring or other ready work.
8. **No scope drift** — out-of-scope change -> new bead, never expand the current one.

## The loop

1. `bd prime` / `bd ready` — load context and actionable work. Load the relevant
   domain skill before editing (`mcb-make-verbs`, `mcb-architecture-layers`,
   `mcb-error-handling`, `mcb-import-rules`, `mcb-testing-patterns`,
   `mcb-quality-gates`) or `mcb-patterns` as the central index.
2. **Re-analyze impact + write a closed spec** for each item before distributing.
3. **Size conflict-free batches**: no two in-flight items touch the same file.
   `makefiles/dispatch.mk` and `Makefile` are a **serial lane** (one owner, sequential).
   Independent lanes (Cargo/config, ci.yml, scripts/hooks, docs) run in parallel.
4. **Dispatch**: each executor takes ONE `bd ready` item, `bd update <id> --claim`
   (atomic lock), exclusive file-ownership. Pick the model by complexity (sonnet for
   impl, haiku for trivial, sonnet/opus for research/verify).
5. **Validate each delivery** (green gate + evidence), then `bd close <id> --reason "evidence"`;
   unblock dependents. Red → reopen, never advance. Run `make check WHAT=guard` before
   any commit that touches `crates/` to catch banned patterns early.
6. Between batches, run `make hook WHAT=pre-push` to catch regressions early.

See `AGENTS.md › Task Tracking (beads / bd)` for the `bd` command surface.

## Multi-agent / multi-session / multi-project (the correct beads model)

Beads is **built for concurrent agents** — collaborate on the shared graph, do NOT
"avoid" another agent's work. Hash-based IDs (`bd-a1b2`) make merges collision-free.

**Concurrency primitives (use, don't fear):**
- `bd update <id> --claim` — atomic ownership (assignee + in_progress). Before editing
  an issue, claim it. If it is already claimed/assigned by another agent, pick a
  different `bd ready` item — that is coordination, not a no-go zone. You MAY work any
  unclaimed item, including across former "lanes".
- Conflicts on the same issue are resolved by the active Dolt backend and the
  command surface exposed by `bd <command> --help`; do not use removed SQLite/
  sync-branch commands from older sessions.

**Sync / backup (Dolt shared-server mode):**
- The authoritative store is Dolt via the shared server reported by
  `bd dolt show --json` / `bd dolt status`. `.beads/issues.jsonl` is a generated
  export for migration/interoperability only. Never hand-edit it.
- Cadence: after bead changes, validate with `bd dolt show --json`,
  `bd backup status --json`, and `bd status --json`. Use `bd dolt commit` /
  `bd dolt push` / `bd dolt pull` or `bd backup` for durable Dolt sync/backup,
  not the removed `bd sync` path.

**Storage mode:**
- MCB uses shared-server mode for multi-writer local concurrency. `bd context`
  still exposes backend identity and may report `dolt_mode: embedded`; treat
  `bd dolt show --json` with `shared_server: true`, `embedded: false`, and
  `connection_ok: true` as authoritative for the active connection mode.
- Embedded (`bd init`, Dolt) is single-writer/single-use only for this workflow.

**Multiple projects:**
- Each project owns its `.beads/` with its own `issue_prefix` (this repo: `mcb`).
  Run `bd` from within the project's repo. Do not store another project's work in
  MCB beads. Use `bd repo list` to verify whether multi-repo hydration is configured;
  otherwise record only local context via `--external-ref` and let the other repo own
  its bead state.
