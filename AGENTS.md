# AGENTS.md — mcb

> **Parent workspace law** lives in [`../AGENTS.md`](../AGENTS.md) — read it first.
> Universal engineering core: `~/.agents/UNIVERSAL_CORE.md`. Composition: global skills + parent/root `AGENTS.md` + this scope delta. Do not re-embed universal law.
>
> **Standalone / independent mode:** when `../AGENTS.md` does not resolve, pin the parent raw `AGENTS.md` URL to the same branch/release as this package (never `main`).

<!-- AIHUB-AGENTS-SCOPE-LOCAL-BEGIN -->
## Commands

The whole dev cycle runs through few canonical `make` verbs backed by the single
monopoly script `scripts/lib/mcb.sh`. Pattern: `make <verb> [WHAT=phase]
[SCOPE=...] [APPLY=Y]`. Do not call `cargo`/`git` directly — use a verb. Run
`make help` for the live list.

```bash
make help                          # All verbs + their WHAT= phases
make build [RELEASE=0|1]           # Release build by default
make dev   [WHAT=run|docker-up|docker-down|docker-logs|docker-test]
make test  [SCOPE=unit|doc|golden|startup|integration|e2e|all] [THREADS=N]
make check [WHAT=fmt|lint|validate|audit|udeps|coverage|qlty|all] [QUICK=1]
make fix   [WHAT=fmt|lint|docs|all]   # Mutating auto-fix (rustfmt, clippy --fix, markdown)
make docs  [WHAT=build|serve|lint|validate|sync|rust|check|setup|adr|adr-new|diagrams] [QUICK=1] [FIX=1]
make ci                            # CI gate (check WHAT=all)
make guard                         # Banned-pattern scanner (prod unwrap/expect/panic/todo, TODO/FIXME, unjustified #[allow])
```

Read-only git / PR / submodule inspection flows through the same monopoly:

```bash
make git WHAT=status|diff|log|show|branch|tags|stash-list
make pr  WHAT=view|checks PR=<n>
make sub WHAT=status|diff
```

Single-test local debugging is allowed when it is materially faster than the
verb:

```bash
cargo test -p mcb-server --test unit -- test_name
```

Destructive verbs are DRY-RUN by default and require `APPLY=Y` to execute:

```bash
make codegen [WHAT=all|cli|db|entities|conversions|clean] APPLY=Y
make release [WHAT=package|version|install|install-validate] [BUMP=patch|minor|major] APPLY=Y
make clean   [WHAT=build|codegen|all] APPLY=Y
make git WHAT=commit MSG='...' [FILES='...'] APPLY=Y   # also push|merge|rebase
make sub WHAT=commit|push SUB=<name> [MSG='...'] APPLY=Y
make setup [WHAT=hooks|tools|adr|all]                  # hooks installs the pre-commit gate
```

`make release WHAT=install APPLY=Y` builds, installs config under the user's home
directory, updates MCP client configs when present, and manages the user `mcb`
systemd service. Run it only when the user explicitly asks for installation work.

Enforcement is mechanical, not honor-system: `make setup WHAT=hooks` installs
no-bypass tiered git hooks driven by one SSOT (`make hook WHAT=pre-commit|pre-push`
in `makefiles/dispatch.mk`). pre-commit (fast): staged `guard` + fmt + clippy
(`--workspace`) + typos + unit tests. pre-push (full): clippy `--all-targets` + full
suite + doctests + `validate quick`, then delegates to the beads `pre-push` hook.
`.claude/settings.json` denies dangerous shell and routes every Bash through
`scripts/lib/mcb.sh guard-bash`; `make guard` scans the full tree (CI/manual) while
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
  and `make git WHAT=status` before editing. Trust `bd context --json` for
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
  beads, subagent state, and `make git WHAT=status`; then it executes or integrates
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
> `make git WHAT=push APPLY=Y` so work is not stranded locally.
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
- Docs-only changes: `make docs WHAT=lint`.
- Public docs plus architecture/status changes: `make docs WHAT=validate QUICK=1`
  when practical.
- Release/install paths: `make release APPLY=Y` only when explicitly requested.

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
<!-- AIHUB-AGENTS-SCOPE-LOCAL-END -->
