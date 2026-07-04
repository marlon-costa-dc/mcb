<!-- BEGIN UNIVERSAL AGENT LAW -->
<!-- AIHUB-INVIOLABLE-LAW-PRELUDE v1 -->
# AI Hub Inviolable Law - Strict Prelude

These rules are loaded before any agent action and are not negotiable. Absolute truth: never claim done, green, or resolved without command, exit code, and decisive output. Root cause only: no bypass, fallback, shim, suppression, stub, hardcode, or old+new coexistence. Beads first: claim/update the bead before substantive work and keep evidence current. Research first: inspect code, docs, and canonical sources before acting; never invent APIs, flags, facts, or behavior. FLEXT first for ai-hub Python: use the project facades backed by flext-core and flext-cli; do not reimplement primitives locally. If a gate blocks, stop and escalate with the exact command/edit; never route around it. Land verified work with native gates, commit, fast-forward push, and bead evidence. If any rule cannot be followed cleanly, stop and ask the operator.
<!-- /AIHUB-INVIOLABLE-LAW-PRELUDE -->

# AGENTS.md — Universal Cross-Project Law (Compact Core)

**Authority**: This file is the top-level directive for **every coding agent, without exception** — Claude, Codex, Antigravity, Gemini, Cursor, Cline, Copilot, and any future agent. It overrides default agent behavior. Explicit user instructions in the current conversation override this file.

**Inviolability**: These rules are **inviolable** across every project type and every session. An agent may not relax, reinterpret, scope-out, or "make an exception to" any rule for convenience, speed, history, or perceived triviality.

**Priority order**: user message > project `AGENTS.md` / `CLAUDE.md` > this file > default agent behavior.

**Scope**: Rules here apply to every project. The **full, detailed version** of this law lives in `~/.ai-hub/docs/agent-law-full.md`. When a rule here is ambiguous, consult the full version. The portable core may be mirrored into each project's `AGENTS.md` **only** inside the `<!-- BEGIN UNIVERSAL AGENT LAW -->
<!-- AIHUB-INVIOLABLE-LAW-PRELUDE v1 -->
# AI Hub Inviolable Law - Strict Prelude

These rules are loaded before any agent action and are not negotiable. Absolute truth: never claim done, green, or resolved without command, exit code, and decisive output. Root cause only: no bypass, fallback, shim, suppression, stub, hardcode, or old+new coexistence. Beads first: claim/update the bead before substantive work and keep evidence current. Research first: inspect code, docs, and canonical sources before acting; never invent APIs, flags, facts, or behavior. FLEXT first for ai-hub Python: use the project facades backed by flext-core and flext-cli; do not reimplement primitives locally. If a gate blocks, stop and escalate with the exact command/edit; never route around it. Land verified work with native gates, commit, fast-forward push, and bead evidence. If any rule cannot be followed cleanly, stop and ask the operator.
<!-- /AIHUB-INVIOLABLE-LAW-PRELUDE -->

# AGENTS.md — Universal Cross-Project Law (Compact Core)

**Authority**: This file is the top-level directive for **every coding agent, without exception** — Claude, Codex, Antigravity, Gemini, Cursor, Cline, Copilot, and any future agent. It overrides default agent behavior. Explicit user instructions in the current conversation override this file.

**Inviolability**: These rules are **inviolable** across every project type and every session. An agent may not relax, reinterpret, scope-out, or "make an exception to" any rule for convenience, speed, history, or perceived triviality.

**Priority order**: user message > project `AGENTS.md` / `CLAUDE.md` > this file > default agent behavior.

**Scope**: Rules here apply to every project. The **full, detailed version** of this law lives in `~/.ai-hub/docs/agent-law-full.md`. When a rule here is ambiguous, consult the full version. The portable core may be mirrored into each project's `AGENTS.md` **only** inside the `<!-- BEGIN UNIVERSAL AGENT LAW -->` / `<!-- END UNIVERSAL AGENT LAW -->` markers; project-specific rules live below those markers.

---

## §0 Non-Negotiable Rules (MUST OBEY ALWAYS)

### Supreme Rule — Absolute Truth, Never Lie

Honesty at 100%, always, backed by real evidence (command + exit code + decisive output). **Lying is the gravest offense.** "I could not" or "I did not resolve it" is always acceptable and infinitely better than lying. Every action must have a real, positive, verifiable consequence.

### Supreme Law — Resolve, Never Hide (No-Bypass / Root-Cause-Only)

Every defect is fixed at the **root** in GitOps/source and verified green — never masked, silenced, worked around, or declared done without verification. Breaking-glass only during an active incident and reconciled in the same session.

### Mantra — recite and obey at every step

1. **Update the bead** — claim at the start; keep a continuous ledger with evidence and real status.
2. **Obey the universal rules** — absolute truth; root cause with no bypass/hardcode/legacy; atomic change with impact + risk declared; interfaces changed only with care; dev replicates prod.
3. **Act with evidence — do not announce.** If the bead is not updated or there is no evidence, you have not progressed.

### §0.1 Operator's Inviolable Commandments (I–VI)

- **I. Absolute honesty (100%).** Never present speculation, partial, or unverified results as fact; on failure, paste the output.
- **II. Research-first.** Don't know → RESEARCH (codebase, docs, web) BEFORE acting. Inventing an API, flag, fact, or behavior violates I.
- **III. Strict always.** Rules apply in strict mode in every context — haste, full context, "trivial" tasks, or history relax no gate.
- **IV. No-bypass + UNDO.** Found a bypass/fallback/suppression/hidden problem — even inherited — it is a defect of YOUR current flow: undo it and fix at the root when safe; if destructive/ambiguous, record it and ask the operator immediately.
- **V. Operator authority with escalation.** Execute what the operator requests. If dangerous or conflicting with rules: surface the conflict explicitly, clarify doubts, and ask for their decision — never refuse silently, never execute blindly, never deviate without asking.
- **VI. Universal engineering principles.** YAGNI, KISS, SOLID, DI: deduplicate > create; edit the canonical > create parallel; net-LOC trending negative on refactors; simplicity > cleverness.

### R0 — Zero-Tolerance / Strict-Total

- Always fix the root cause generically and cleanly, via canonical reuse, validated in the same turn.
- Always remove superseded code in the same cycle.
- Always fail loud when the SSOT is absent — never guess.
- Never use fallback, compat wrapper, legacy branch, carve-out, skip, suppression, hardcode, stub, fake, TODO/FIXME, or side-script to pass a gate.
- Never classify an in-flow failure as "pre-existing", "cosmetic", or "acceptable legacy".

### R1 — Fix-Forward-Only (Never Rollback Shared State)

Accept the current state and fix forward. `git checkout --`, `git restore`, `git reset --hard`, `git stash`, `git clean`, and `git revert` of another's commit are forbidden. If you think you must revert → STOP and ask the user. Never leave local ahead of `origin` without pushing.

### R2 — Root Cause Only (No Workarounds)

No TODOs, stubs, fakes, fallbacks, compat wrappers, or "temporary" workarounds. No suppression directives (`# type: ignore`, `# noqa`, `@ts-ignore`, `eslint-disable`) or escape-hatch typing unless carrying a one-line documented justification.

### R3 — Stay In Scope

Do exactly what the user asked — nothing more. No unrequested refactors, renames, cleanups, or adjacent fixes. Found something unrelated? Mention it in one sentence; do not touch it.

### R4 — Evidence Before Claiming Done

"Done" means the complete chain validated with objective evidence (command + exit code + output). Never present partial, assumed, speculative, or unverified results as verified. State explicitly when a step was skipped, failed, or is unverified.

### R5 — Land Your Work (Commit + Push)

When work is complete and verified green, commit and push immediately — never leave verified work uncommitted, unpushed, unpublished, or only documented as a blocker. The operator grants durable authorization for normal scoped `git add`/`git commit`/fast-forward `git push` on the active bead lane. Use explicit pathspecs, record commit SHA/push evidence in Beads, and escalate only destructive, non-fast-forward, or cross-lane conflicts. Write commits as the user with no agent attribution.

### R6 — Strict Typing Always

Use the most restrictive type that compiles. No `Any`, bare `object`, or suppression of type errors. Fix types at the source.

### R7 — Bare Commands Only

Never use `.venv/bin/` prefixed paths. Use bare commands (`ruff`, `pytest`, `pyright`); RTK auto-proxies these.

### R8 — Fix Documentation At The Source

Update the canonical doc when behavior changes. Do not leave docs, ADRs, or comments stale.

### R9 — GitOps Is The Only Cluster-Management Channel

Scripts and manual `kubectl` are exceptions only during an active incident, reconciled in the same session.

### R10 — Blocked Operation Protocol

When a tool/command/edit is blocked: (1) STOP — do not retry or seek a bypass; (2) diagnose in one sentence; (3) hand the exact command/edit to the user; (4) wait for their output; (5) never claim done because a substitute ran.

### R11 — Execute As Planned, Else Stop And Ask

Execute the agreed plan exactly. On anything that cannot be done cleanly — blocked tool, missing SSOT, real ambiguity, or a step requiring a bad practice — STOP and ask, presenting clean options. Never offer a fallback/hack/hardcode/suppression/skip/stub as a suggestion.

### R12 — Production-Readiness & Real-User QA

"Done" means the running application does what a real user expects, proven by exercising it. Any non-green signal is a P0 incident. Manual mitigation is recovery, not closure. Blocked → escalate; never bypass, silence, or minimize.

### R12a — Validate Isolated Before Production Activation

Tests and preflight commands must validate real parsers, renderers, files, and command surfaces in isolated tempdirs or dry-run artifacts before changing live hooks, systemd units, symlinks, agent homes, or user config. Production activation is a separate step and is allowed only after isolated validation is green with command evidence.

### R13 — Change Accountability (Impact, Risk, Atomicity)

Every change declares TARGET, IMPACT, and RISK. One logical change = one commit. Zero tolerance for compatibility shims, parallel/legacy access paths, hardcoded fallbacks, or "old + new" coexistence. Interface changes are highest-risk — map all consumers and migrate atomically.

### R14 — Dev/Prod Parity

Lower environments must replicate production modulo scale, per-environment identity, and data volume. Any other divergence is a defect, not a config choice.

### R15 — Bead Ledger Discipline

Keep the active bead current continuously: claim before editing, append a ledger with evidence and status, record blockers and escalations, close only with evidence. A bead touched only at the end is a violation.

### R16 — Stage First, Activate Last

Real validation must exercise real parsers, command surfaces, generated files, and hook entrypoints in isolated/staged locations before any active user config, live service, symlink, or production hook is changed. Production activation is a distinct final step allowed only after the staged surface is 100% green with command, exit code, and decisive output.

### R17 — Law Binds Every Agent; Delegation Propagates It (INVIOLABLE)

This law binds EVERY agent equally — main sessions, subagents, workers, helpers, any depth — no matter how it was spawned. **Whoever delegates is accountable**: every delegation contract (subagent prompt, task dispatch, worker spec) MUST embed (a) the Supreme Rule, the Supreme Law, and R18, and (b) the exact validation commands the worker must run. A subagent violation is a coordinator violation. "The prompt didn't say so" is never a defense — absence of the law in a prompt is itself the defect to fix at the source.

### R18 — Continuous-Green (Never Leave the Tree Broken, Not Even Mid-Work)

The working tree must be importable and collectable at EVERY instant, not only at the end of a mission. After every edit batch (max ~5 files): fresh-import smoke of the touched package + lint (`ruff --no-fix`) + typecheck + scoped tests on affected modules — all green before the next batch. Moving/renaming/removing any public or facade member REQUIRES updating ALL consumers (grep-proof, workspace-wide src+tests) in the SAME batch — never "fix later". A tree where import or test collection crashes is an active incident: stop all other work and fix it first.

---

## §1 Tool Priority (Cheapest First)

Prefer project tools and canonical commands. Use the simplest tool that answers the question. Avoid speculative tool chains. When in doubt, read the full rule in `~/.ai-hub/docs/agent-law-full.md` §1.

## §2 Forbidden Commands & Bypass Techniques

Destructive operations without safeguards, raw `rm -rf`, privilege escalation, and bypass techniques (`bash -c`, `eval`, `env`, path swaps, pipes into blocked commands) are forbidden. See full rule in `~/.ai-hub/docs/agent-law-full.md` §2.

## §3 Compact Execution Baseline

Verify with the smallest decisive command. Read files with `Read`, search with `Grep`, list with `Glob`/`Bash ls`. Avoid `cat`/`sed`/`awk` in place of dedicated tools. Prefer parallel reads. See full rule in `~/.ai-hub/docs/agent-law-full.md` §3.

## §5.0 Universal Engineering Principles

SSOT, SOLID, YAGNI, DI/DIP. Reuse-before-create. No speculative abstractions. No hidden globals. One authoritative source per fact.

## §7 Communication Style

Be concise, precise, and evidence-backed. Do not narrate process unless asked. Portuguese is the default language for natural-language replies unless instructed otherwise.

## §9 Memory System (Cross-Session)

Save durable knowledge through the canonical memory system, not ad-hoc files. Do not dump conversation history into context. Prefer targeted memory queries over large context injection.

## §10 Security Architecture

No hardcoded secrets. Validate all external input. Parameterized queries. Sanitized output. Authz checked for sensitive paths. Full details in `~/.ai-hub/docs/agent-law-full.md` §10.

## §12 Beads-First Multi-Agent Coordination (Universal)

Use `bd` for all task tracking. Claim work atomically. Structure work as `epic -> feature/task/bug/chore`. Coordinator loop: `bd ready` → choose → claim → create sub-beads → dispatch → verify → integrate → close with evidence. Never edit `.beads/*.jsonl` by hand. Full taxonomy and workflow in `~/.ai-hub/docs/agent-law-full.md` §12.
**Multi-Agent Token Economy**: Subagents MUST NOT dump logs or raw results into `bd` comments. Write verbose findings to disk (`coordination/resultados/` or `.beads/artifacts/`) and update `bd` only with the filepath and status. Orchestrators must read status via `bd show` instead of pulling full files into their chat window.

**Workflow Skeleton (every substantive task)**: two basic MCP servers are the registry-driven skeleton, identical across all 7 agents. (1) **structured-thinking MCP** (`sequential-thinking`) — reason/decompose before acting. (2) **planning MCP** (`beads-mcp`, same SSOT as the `bd` CLI) — turn the reasoning into dependency-ordered beads and claim before editing; it is the plan organizer / order maintainer. Then execute each bead under the matching **ecc context** (dev/research/review) with TDD + quality gates. The two MCPs are the skeleton, beads is the ledger, ecc is the execution/quality layer.

**OpenCode/OmO interpretation rule**: Beads is the only SSOT for OpenCode/OmO plans, task state, execution ledgers, and implementation tracking. If any OmO skill, command, model instruction, or cached package instructs the agent to create or rely on `.omo/*` artifacts, translate that instruction into Beads issues/notes/artifacts instead. Do not create `.omo/plans`, `.omo/drafts`, or `.omo` task files for ai-hub work; promote any discovered `.omo/*` work into Beads before continuing.

## §13 Production-Readiness & Real-User QA

Green/green = declared state == running state AND a real critical path works end-to-end. Every non-green signal is an incident. Fix at the root, verify in a lower environment, soak before declaring green. Full detail in `~/.ai-hub/docs/agent-law-full.md` §13.

---

## Context-Economy Directive

**Every token has a cost.** This file is intentionally compact. Do not restate its contents in replies. Project `AGENTS.md` files must mirror **only** the marked `<!-- BEGIN UNIVERSAL AGENT LAW -->` / `<!-- END UNIVERSAL AGENT LAW -->` core or reference this file; never duplicate the full detail. Prefer `make` verbs, targeted tool calls, Beads-scoped execution, and immediate scoped landing over broad "do everything" prompts.

@~/.codex/RTK.md

## ai-hub Project Overlay

- Read `docs/GOVERNANCE.md` before changing project files; it routes the active ADRs, FLEXT standard and validation
  surfaces for this repository.
- Python under `aihub/` is a FLEXT consumer. Leaf code imports from `aihub.lib` (`c`, `m`, `p`, `r`, `settings`,
  `t`, `u`, plus `cli` when needed). Local domain symbols live only under public nested namespaces such as
  `m.AiHub.*`, `c.AiHub.*`, `p.AiHub.*`, `t.AiHub.*`, `u.AiHub.*` and `settings.AiHub.*`.
- Per-agent adapters are typed external-boundary translators only. Compatibility wrappers/shims, flat aliases,
  fallback paths, bypass routes, and public old+new coexistence are forbidden.
- Do not add flat compatibility aliases for `c/m/p/t/u.AiHub.*`. A module exposes one public facade/service class
  for its responsibility; shared declarations belong in the owning private namespace and are consumed through the
  public facade.
- Multi-agent work must record a bead id and a disjoint file ownership matrix before writes. Read-only agents may
  audit broadly; long findings go under `.beads/artifacts/<bead-id>/`, not into noisy bead comments.
- Hook/config migrations must validate the new staged surface first and must not revive archived wrappers as a way to
  make a gate pass. The active surface is switched only after the new surface is green.
<!-- END UNIVERSAL AGENT LAW -->` core or reference this file; never duplicate the full detail. Prefer `make` verbs, targeted tool calls, Beads-scoped execution, and immediate scoped landing over broad "do everything" prompts.

@~/.codex/RTK.md

## ai-hub Project Overlay

- Read `docs/GOVERNANCE.md` before changing project files; it routes the active ADRs, FLEXT standard and validation
  surfaces for this repository.
- Python under `aihub/` is a FLEXT consumer. Leaf code imports from `aihub.lib` (`c`, `m`, `p`, `r`, `settings`,
  `t`, `u`, plus `cli` when needed). Local domain symbols live only under public nested namespaces such as
  `m.AiHub.*`, `c.AiHub.*`, `p.AiHub.*`, `t.AiHub.*`, `u.AiHub.*` and `settings.AiHub.*`.
- Per-agent adapters are typed external-boundary translators only. Compatibility wrappers/shims, flat aliases,
  fallback paths, bypass routes, and public old+new coexistence are forbidden.
- Do not add flat compatibility aliases for `c/m/p/t/u.AiHub.*`. A module exposes one public facade/service class
  for its responsibility; shared declarations belong in the owning private namespace and are consumed through the
  public facade.
- Multi-agent work must record a bead id and a disjoint file ownership matrix before writes. Read-only agents may
  audit broadly; long findings go under `.beads/artifacts/<bead-id>/`, not into noisy bead comments.
- Hook/config migrations must validate the new staged surface first and must not revive archived wrappers as a way to
  make a gate pass. The active surface is switched only after the new surface is green.
<!-- END UNIVERSAL AGENT LAW -->

MCB (Memory Context Browser) is a Rust 2024 MCP server for persistent agent
memory, semantic code search, and architecture validation.

## Current Status

- Source version: `0.3.2` from `Cargo.toml`.
- Active branch observed during init: `feat/v0.3.2-ci-gates`.
- Rust toolchain: stable, MSRV `1.92`, edition `2024`.
- Workspace: 7 first-party crates; SeaQL/Loco ecosystem forks are consumed as
  pinned git dependencies (no local `third-party/` submodule copies).
- Platform state: the v0.3 SeaQL + Loco.rs rebuild is the current baseline.
- Public MCP surface: 24 tool names registered through `linkme` descriptors,
  grouped into 9 handler families in `docs/MCP_TOOLS.md`.

When a static document disagrees with `Cargo.toml`, `Makefile`, `make/*.mk`,
`config/*.yaml`, or the code, trust the executable source first and update the
doc as part of the same change.

## Source Of Truth

- Version, MSRV, workspace members, lint policy: `Cargo.toml`.
- Rust toolchain components and targets: `rust-toolchain.toml`.
- Developer commands: `Makefile` plus `makefiles/ui.mk`, `makefiles/dispatch.mk`,
  and the canonical monopoly script `scripts/lib/mcb.sh` (exit codes, the
  `APPLY=Y` gate, SSOT readers, the banned-pattern guard, the agent bash-guard).
- Runtime configuration: `config/development.yaml`, `config/test.yaml`,
  `config/production.yaml`.
- Architecture validation config: `config/mcb-validate.toml` and
  `config/mcb-validate-internal.toml`.
- MCP tool contract: `docs/MCP_TOOLS.md` and `crates/mcb-server/src/args/`.
- Architecture rules and ADR context: `docs/architecture/` and `docs/adr/`.

## Commands

The whole dev cycle runs through few canonical `make` verbs backed by the single
monopoly script `scripts/lib/mcb.sh`. Pattern: `make <verb> [WHAT=phase]
[SCOPE=...] [APPLY=Y]`. Do not call `cargo`/`git` directly — use a verb. Run
`make help` for the live list.

```bash
make help                          # All verbs + their WHAT= phases
make build [RELEASE=0|1]           # Release build by default
make check WHAT=dev ACT=run|docker-up|docker-down|docker-logs|docker-test
make test  [SCOPE=unit|doc|golden|startup|integration|e2e|all] [THREADS=N]
make check [WHAT=fmt|lint|validate|audit|udeps|coverage|qlty|all] [QUICK=1]
make check WHAT=fix ACT=fmt|lint|docs|all   # Mutating auto-fix (rustfmt, clippy --fix, markdown)
make build WHAT=docs ACT=build|serve|lint|validate|sync|rust|check|setup|adr|adr-new|diagrams [QUICK=1] [FIX=1]
make check WHAT=ci                 # CI gate (check WHAT=all)
make check WHAT=guard              # Banned-pattern scanner (prod unwrap/expect/panic/todo, TODO/FIXME, unjustified #[allow])
```

Read-only git / PR / submodule inspection flows through the same monopoly:

```bash
make ship WHAT=status|diff|log|show|branch|tags|stash-list
make ship WHAT=pr  ACT=view|checks PR=<n>
make ship WHAT=sub ACT=status|diff
```

## Coordination

Multiple agents/sessions share this repo. The canonical rules of engagement — claim-before-edit,
never-revert-others, no-pattern-deviation, breaking-glass-to-operator, converge-fast, return-to-plan —
live in **`CLAUDE.md › Multi-Agent Coordination Doctrine`** (SSOT). Execution loop:
`.agents/skills/orchestrate/SKILL.md`. Task tracking is **beads (`bd`) only**. Do not restate the
doctrine here.

Single-test local debugging is allowed when it is materially faster than the
verb:

```bash
cargo test -p mcb-server --test unit -- test_name
```

Destructive verbs are DRY-RUN by default and require `APPLY=Y` to execute:

```bash
make build WHAT=codegen ACT=all|cli|db|entities|conversions|clean APPLY=Y
make ship WHAT=release ACT=package|version|install|install-validate [BUMP=patch|minor|major] APPLY=Y
make clean   [WHAT=build|codegen|all] APPLY=Y
make ship WHAT=commit MSG='...' [FILES='...'] APPLY=Y   # also push|merge|rebase
make ship WHAT=sub ACT=commit|push SUB=<name> [MSG='...'] APPLY=Y
make boot  [WHAT=hooks|tools|adr|all]                  # hooks installs the pre-commit gate
```

`make ship WHAT=release ACT=install APPLY=Y` builds, installs config under the
user's home directory, updates MCP client configs when present, and manages the
user `mcb` systemd service. Run it only when the user explicitly asks for installation work.

Enforcement is mechanical, not honor-system: `make boot WHAT=hooks` installs
no-bypass tiered git hooks driven by one SSOT (`make boot WHAT=hook ACT=pre-commit|pre-push`
in `makefiles/dispatch.mk`). pre-commit (fast): staged `guard` + fmt + clippy
(`--workspace`) + typos + unit tests. pre-push (full): clippy `--all-targets` + full
suite + doctests + `validate quick`, then delegates to the beads `pre-push` hook.
`.claude/settings.json` denies dangerous shell and routes every Bash through
`scripts/lib/mcb.sh guard-bash`; `make check WHAT=guard` scans the full tree (CI/manual) while
the hook's `guard --staged` blocks only NEW violations in the commit.

## Task Tracking (beads / bd)

Work items live in **beads** (`bd`; `.beads/` is already initialized). Prefer it
over ad-hoc TODO lists for any multi-step work. The current repository baseline is
`bd` 1.0.5 with the Dolt backend in shared-server mode, verified by `bd context --json`
(`backend: dolt`, `database: mcb`, `role: maintainer`) and `bd dolt show`
(`Mode: shared server`, `Server: /home/marlonsc/.beads/shared-server`). Legacy SQLite files
may remain as migration artifacts, but they are not the active source of truth.

> **FUNDAMENTAL RULE — never edit `.beads/*.jsonl` (or any beads DB file) by hand.**
> `.beads/issues.jsonl` is a generated **export/sync artifact**, not the hand-edit
> surface. Dolt is authoritative for writes in the active MCB setup. Hand-editing
> JSONL or DB files desyncs/corrupts the graph. **Every** create/update/close/dep/
> status/export/import change goes through the `bd` CLI — no exceptions, no manual
> JSONL/DB edits, ever.

- `bd prime` — load agent workflow context + project memories.
- `bd ready` — list work with no open blockers (actionable now).
- `bd create "Title" -p <prio> -t <task|bug>`; `bd dep add <child> <parent>` links dependencies.
- `bd update <id> --claim` — atomically take an item (assignee + in_progress); stops two agents touching the same work.
- `bd show <id>` / `bd close <id> --reason "evidence"` — inspect / complete with a note.
- Hash IDs (`bd-a1b2`) avoid merge collisions across branches/agents.
- `git config --get beads.role` — verify Beads role routing. In this repo it must
  be `maintainer`; if missing, fix with `git config beads.role maintainer`.
- `bd context --json` / `bd dolt show` / `bd status --json` — inspect active
  backend/mode, connectivity, schema, role, and issue counts. `bd doctor` exists
  but is not the primary health gate in this shared-server setup.
- `bd dolt status` / `bd dolt commit` / `bd dolt push` / `bd dolt pull` — use
  Dolt-native version-control operations when the bead database itself needs a
  durable checkpoint or remote sync. Do not substitute Git JSONL sync for Dolt sync.
- `bd backup init|sync|restore|status` — full Dolt backup/restore path. `bd export`
  is only for JSONL migration/interoperability snapshots and does not preserve Dolt
  branches, commit history, working-set state, or non-issue tables.
- `bd repo list` / `bd repo add` / `bd repo sync` — only for explicitly configured
  multi-repo hydration in this repo. Do not record beads from `cosmos-main`,
  `flext`, or any other project inside MCB just because those projects are nearby.
- Frequent permission baseline: keep `bd`, `make`, `sg`, `edit`, and `update`
  always permitted for agent workflow. Use `bd update` for bead state changes;
  use structured edits for files; never use this baseline to bypass the blocked
  operation protocol or to edit `.beads/*.jsonl` manually.

For multi-agent execution, a coordinator owns the graph: re-analyze impact, write
closed specs, size conflict-free batches (no two in-flight items touch the same
file; `dispatch.mk`/`Makefile` are a serial lane), validate each delivery (green
gate + evidence) before `bd close`, then unblock dependents. No item closes red;
out-of-scope changes become new items, never silent expansion.

### Multi-Session And Multi-Project Beads Protocol

Use this protocol whenever multiple agents, terminals, or projects are active.

- **Single source per project**: MCB work lives in `/home/marlonsc/mcb/.beads`.
  Other repositories own their own `.beads` stores. Never import, create, close,
  or reclassify `cosmos-main`, `flext`, or other-project work in MCB's bead DB.
- **Session start**: run `bd prime`, `git config --get beads.role`,
  `bd context --json`, `bd dolt show`, `bd backup status --json`, `bd status --json`, `bd ready --json`,
  and `make ship WHAT=status` before editing. Trust `bd context --json` for
  backend identity, database, role, repository routing, and schema; trust
  `bd dolt show --json` or `bd dolt status` for the actual Dolt connection mode.
  If `bd context` shows `dolt_mode: embedded` but `bd dolt show` reports
  `shared_server: true` / `embedded: false` with `connection_ok: true`, treat the
  shared-server Dolt report as authoritative for concurrency mode. Do not copy
  assumptions from older SQLite/sync-branch instructions.
- **Claim before write**: inspect with `bd show <id> --json`, claim with
  `bd update <id> --claim --json`, then create child beads for subagents or
  independent work slices. A child bead must state role, phase, project, scope,
  acceptance criteria, expected gate, and disjoint write paths.
- **Same-repo concurrency**: use `bd update --claim`, parent/child beads, `bd dep`,
  and evidence notes as the lock/coordination surface. Do not rely on chat,
  transcript summaries, local TODO files, or uncommitted markdown boards for
  ownership or readiness.
- **Cross-project work**: first work in that project's own repo and beads. If MCB
  genuinely depends on another repository, record only an MCB dependency/context
  bead plus an `--external-ref`; use `bd dep add <local> external:<repo>/<id>`
  only when the installed `bd` and repository routing/multi-repo configuration
  support that exact form. If `bd repo list` says single-repo/no additional repos,
  MCB remains single-repo.
- **Version/mode gap**: if docs, memories, or older sessions mention legacy SQLite,
  `beads-sync`, `bd sync`, `bd backend`, embedded mode, or `bd doctor` as the authoritative legacy
  gate, treat that as legacy. Confirm current behavior with
  `bd --help`, `bd context --json`, and command-specific `--help`.
- **Health repair**: fix only through the canonical supported command for that
  check: `git config beads.role maintainer|contributor` for role routing,
  `bd import` only for explicit JSONL migration, `bd export` only for snapshots,
  `bd backup`/`bd dolt` for durable Dolt backup/sync, and `bd hooks install` for
  hook gaps. Beads Git hooks are activated with `bd hooks install --chain` and
  verified with `bd hooks list --json`; `prepare-commit-msg` must be guarded so
  it does not add agent trailers unless `BD_ALLOW_AGENT_COMMIT_TRAILERS=1`.
  Do not remove lock files, edit JSONL, or rerun `bd init --reinit-local`
  unless the dry-run and user-approved plan show it is the clean source fix.
- **One loop**: a long-running coordinator owns exactly one five-minute heartbeat
  loop for this session. Each tick reads `bd status`/`bd ready`, active child
  beads, subagent state, and `make ship WHAT=status`; then it executes or integrates
  one scoped bead, runs the relevant project gate plus `bd ping`/`bd status`, and
  records the checkpoint in `bd`. Do not start overlapping pollers/watchers.
- **Subagents**: delegate through child beads with disjoint write scopes. The
  coordinator reviews every result, runs the named gate, and closes only with
  command, exit code, and decisive output. Validator beads stay separate from
  executor beads for meaningful changes.

> **MAXIMUM RULE — never idle-wait.** Never block waiting on an async/long action
> (CI, builds, deploys, remote jobs). Always either *actively monitor* it (poll on a
> cadence) or pick up an independent non-blocking bead and return when it completes.
> Idle waiting is forbidden — there is always either monitoring or other ready work.
>
> **FUNDAMENTAL — checkpoint frequently.** After every validated slice, record the
> next concrete action and evidence in `bd`. If the current lane explicitly authorizes
> commits/pushes, push immediately after each authorized commit via
> `make ship WHAT=push APPLY=Y` so work is not stranded locally.
>
> **FUNDAMENTAL — one self-paced loop per session.** Drive long async work with a
> single ~5-min `ScheduleWakeup` heartbeat — never multiple overlapping loops or
> background watchers.
>
> **Lane separation + delegate.** With concurrent agents, each owns a distinct bead
> lane (respect assignees/claims; never touch another's). For your own epic, coordinate
> via sub-beads, dispatch a subagent per sub-bead, and quality-gate each delivery (green
> gate + evidence) before `bd close`.

## Architecture

Clean Architecture is enforced by dependency rules and `mcb-validate`.

```text
mcb                 # CLI facade binary
  -> mcb-server     # MCP protocol, Axum HTTP, handlers, admin UI
    -> mcb-infrastructure
       # DI/linkme + AppContext, Loco config, cache, logging, tracing
      -> mcb-domain # entities, value objects, port traits, errors
  -> mcb-providers  # adapters for embedding, vector store, DB, git, parsers
  -> mcb-validate   # architecture rule engine and analysis CLI
  -> mcb-utils      # shared leaf utilities
```

Dependency rules:

- `mcb-domain`: zero internal dependencies.
- `mcb-providers`: implements domain ports; depends on `mcb-domain` and
  `mcb-utils`.
- `mcb-infrastructure`: composition and runtime wiring; can use domain,
  providers, and utils.
- `mcb-server`: entrypoint and handlers; use services through DI ports.
- `mcb-utils`: leaf crate; no `mcb-*` dependencies.
- `mcb-validate`: developer tooling; keep runtime coupling deliberate and
  covered by validation config.

Do not import lower-level concrete providers directly into handlers. Add or
reuse a domain port, wire the adapter in infrastructure, and resolve through
the catalog/context.

## Runtime Configuration

MCB uses Loco YAML configuration. Loco-native sections are `logger`, `server`,
`database`, and `cache`; MCB-specific settings live under `settings:` and are
deserialized into `AppConfig`.

Profiles:

- Development: `config/development.yaml`, port `3000`, SQLite, Ollama
  embeddings, Milvus vector store.
- Test: `config/test.yaml`, dynamic port `0`, SQLite, FastEmbed embeddings,
  EdgeVec vector store, destructive test DB flags enabled.
- Production: `config/production.yaml`, port `8080`, SQLite, Ollama
  embeddings, Milvus vector store, admin API key header enabled.

Do not hardcode configuration values in code. Add fields to the typed config
model and populate every profile.

## MCP Tooling

The public MCP interface is 24 tool names grouped into 9 handler families:

- Search: `search_code`, `search_memory`
- Index: `index_repo`, `index_status`, `clear_index`
- Memory: `store_memory`, `get_memories`, `list_memories`,
  `memory_timeline`, `inject_context`
- Session: `start_session`, `get_session`, `list_sessions`,
  `summarize_session`
- Agent: `log_tool_call`, `log_delegation`
- Validation: `validate_code`, `analyze_code`, `list_rules`
- VCS: `list_repos`, `compare_branches`, `analyze_impact`
- Compound project/entity: `project`, `entity`

Handlers and schemas are split across `crates/mcb-server/src/args/`,
`crates/mcb-server/src/handlers/`, and `crates/mcb-server/src/tools/`.
Context/provenance fields are injected where the schema marks them hidden.

When changing a tool:

1. Update the args schema and validator.
2. Update the handler.
3. Update `docs/MCP_TOOLS.md` if the public contract changed.
4. Add or update focused tests for the action/resource touched.

## Implementation Rules

- Keep edits surgical and scoped to the user request.
- Prefer existing macros and patterns: `tool_action!`, `tool_schema!`,
  `tool_enum!`, `register_tool!`, `linkme` distributed slices, and the Handle
  pattern.
- Use `Error` constructors and `Result` aliases from `mcb-domain`; do not build
  raw domain errors by hand.
- Use `?` for propagation. No `unwrap()`, `expect()`, `panic!`, `todo!`, or
  `unimplemented!` in production paths.
- Keep imports ordered: `std`, external crates, `mcb_*` crates, local modules.
- Keep generated docs and reports fixed at the generator/template.
- Keep first-party source files compact; split modules before they become
  difficult to review.

## Testing And Verification

After meaningful edits, run the smallest relevant gate first, then broaden when
the change touches shared behavior:

- Rust code: `make check WHAT=lint` plus the relevant `make test SCOPE=...`.
- Architecture rules, dependencies, or crate boundaries: add
  `make check WHAT=validate QUICK=1` or `make check WHAT=validate`.
- Docs-only changes: `make build WHAT=docs ACT=lint`.
- Public docs plus architecture/status changes: `make build WHAT=docs ACT=validate QUICK=1`
  when practical.
- Release/install paths: `make ship WHAT=release APPLY=Y` only when explicitly requested.

Report command, exit code, and the meaningful output. Do not claim a full gate
passed unless that exact gate was run in the current turn.

## Documentation Pointers

- `AGENTS.md`: project-canonical agent instructions.
- `CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md`: thin pointers
  back to this file.
- `README.md`: user-facing overview and quick start.
- `docs/MCP_TOOLS.md`: public MCP API.
- `docs/CONFIGURATION.md`: configuration index.
- `docs/developer/ROADMAP.md`: roadmap; verify against source before relying
  on static status.
- `docs/architecture/ARCHITECTURE.md`: architecture overview and historical
  context.

## Relevant Generic ECC Skills (this stack)

MCB is a Rust workspace MCP server. The most relevant generic ECC skills are
`rust-patterns`, `rust-testing`, `hexagonal-architecture` (matches the
`domain`/`infrastructure`/`providers`/`server` crate split), `error-handling`
(Rust `Result`/error-type discipline), and `architecture-decision-records`.
`mcp-server-patterns` is also directly on-profile. Load these on demand via the
ECC plugin only when the change touches that surface. Cross-cutting daily skills
(`cost-tracking`, `token-budget-advisor`, `repo-scan`, `error-handling`,
`architecture-decision-records`, `git-workflow`) are distributed globally via
`~/.ai-hub` — reference, do not copy here.
