---
name: mcb-import-rules
description: Import ordering, visibility, and crate boundary rules for MCB. Use when adding imports, resolving circular dependencies, or reviewing module visibility.
license: MIT
metadata:
  version: 1.0.0
---

# MCB Import Rules

**UTILITY SKILL**

Import hygiene and visibility rules for the MCB Rust workspace.

## USE FOR

- Adding or reorganizing imports.
- Resolving circular imports.
- Reviewing `pub`/`pub(crate)` visibility.

## DO NOT USE FOR

- Questions unrelated to MCB imports.
- Generic Rust style outside MCB.

## Critical rules

- Import order is enforced by rustfmt:
  1. `std`
  2. external crates
  3. `mcb_*` workspace crates
  4. `crate::` local modules
- `lib.rs` is the public API hub: declare modules and re-export key types.
- Prefer `pub(crate)` for internal items; private by default.
- Do not import concrete providers into handlers; use domain ports + DI.

## Good examples

### Import order

```rust
use std::sync::Arc;

use serde::{Deserialize, Serialize};
use tokio::sync::RwLock;

use mcb_domain::ports::providers::EmbeddingProvider;
use mcb_utils::id::generate_id;

use crate::config::AppConfig;
```

### lib.rs as hub

```rust
// mcb-domain/src/lib.rs
pub mod entities;
pub mod error;
pub mod macros;
pub mod ports;
pub mod value_objects;

pub use entities::*;
pub use error::{Error, Result};
```

## Bad examples

### Concrete provider in handler

```rust
// WRONG
use mcb_providers::embedding::openai::OpenAiEmbedding;
```

### Mixed import groups

```rust
// WRONG
use crate::config::AppConfig;
use mcb_domain::Error;
use std::sync::Arc;
```

### Wildcard imports outside lib.rs

```rust
// WRONG outside lib.rs
use mcb_domain::*;
```

## Visibility guide

| Visibility | Use when |
|------------|----------|
| `pub` | Public API surface (lib.rs re-exports) |
| `pub(crate)` | Internal to the crate |
| private | Internal to the module |
| `pub(super)` | Internal to the parent module |

## Re-export pattern

Each crate exposes a focused public surface:

```rust
// mcb-providers/src/lib.rs
pub mod embedding;
pub mod vector_store;

pub use embedding::{EmbeddingProvider, EmbeddingConfig};
```

## Verification

```bash
make check WHAT=fix ACT=fmt APPLY=Y   # rustfmt
make check WHAT=lint                   # clippy + fmt check
```

## References

- `docs/developer/CONTRIBUTING.md` — naming conventions and file organization.
- `docs/architecture/PATTERNS.md` — module organization patterns.
