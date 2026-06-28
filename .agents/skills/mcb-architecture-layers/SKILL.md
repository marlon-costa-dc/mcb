---
name: mcb-architecture-layers
description: Clean Architecture crate boundaries and dependency rules for MCB. Use when adding modules, moving responsibilities, or reviewing imports across crates.
license: MIT
metadata:
  version: 1.0.0
---

# MCB Architecture Layers

**UTILITY SKILL**

Clean Architecture / Hexagonal dependency rules for the MCB Rust workspace.

## USE FOR

- Adding modules, moving responsibilities, or reviewing imports.
- Verifying a change does not violate crate boundaries.

## DO NOT USE FOR

- Questions unrelated to MCB architecture.
- Creating projects from scratch.

## Critical rules

- Dependency direction is one-way inward:
  `mcb-server → mcb-infrastructure → mcb-providers → mcb-domain`.
- `mcb-utils` is a leaf crate: no `mcb-*` dependencies.
- `mcb-validate` is developer tooling; keep runtime coupling deliberate.

## Crate map

| Crate | Role | May depend on |
|-------|------|---------------|
| `mcb` | CLI facade binary | `mcb-server`, `mcb-providers`, `mcb-validate`, `mcb-utils` |
| `mcb-server` | MCP protocol, Axum HTTP, handlers, admin UI | `mcb-infrastructure`, `mcb-domain`, `mcb-utils` |
| `mcb-infrastructure` | DI/linkme, AppContext, Loco config, cache, logging, tracing | `mcb-providers`, `mcb-domain`, `mcb-utils` |
| `mcb-providers` | Adapters for embedding, vector store, DB, git, parsers | `mcb-domain`, `mcb-utils` |
| `mcb-domain` | Entities, value objects, port traits, errors, macros | `mcb-utils` only |
| `mcb-utils` | Shared leaf utilities | none (`mcb-*`) |
| `mcb-validate` | Architecture rule engine and CLI | workspace crates as needed |

## Good examples

### Handler uses a domain port via DI

```rust
// mcb-server/src/handlers/search.rs
use mcb_domain::ports::providers::EmbeddingProvider;
use mcb_infrastructure::di::Handle;

pub struct SearchHandler {
    embedding: Handle<dyn EmbeddingProvider>,
}
```

### Provider implements a domain port

```rust
// mcb-providers/src/embedding/openai.rs
use mcb_domain::ports::providers::EmbeddingProvider;

#[async_trait]
impl EmbeddingProvider for OpenAiEmbedding {
    async fn embed(&self, text: &str) -> Result<Embedding> { ... }
}
```

## Bad examples

### Handler imports a concrete provider

```rust
// WRONG: handler bypasses the port
use mcb_providers::embedding::openai::OpenAiEmbedding;
```

### Domain depends on infrastructure

```rust
// WRONG: domain must not know about infrastructure
use mcb_infrastructure::config::AppConfig;
```

### Port trait declared outside mcb-domain

```rust
// WRONG: ports live in mcb-domain/src/ports/**
pub trait NewProvider { ... }
```

## Adding a new provider

1. Define the port trait in `mcb-domain/src/ports/providers/<name>.rs`.
2. Implement the trait in `mcb-providers/src/<name>/<impl>.rs`.
3. Register the implementation with `impl_registry!` + `#[distributed_slice]`.
4. Wire the resolved provider in `mcb-infrastructure::di::bootstrap::init_app`.
5. Inject `Handle<dyn Trait>` into handlers/services.

## Verification

```bash
make check WHAT=validate QUICK=1
```

## References

- `docs/architecture/PATTERNS.md` — detailed patterns.
- `docs/architecture/ARCHITECTURE_BOUNDARIES.md` — boundary enforcement rules.
- `Cargo.toml` — workspace members and dependency SSOT.
