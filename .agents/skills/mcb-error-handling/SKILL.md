---
name: mcb-error-handling
description: Typed error handling, propagation, and logging rules for MCB. Use when writing or reviewing Rust error paths in the MCB workspace.
license: MIT
metadata:
  version: 1.0.0
---

# MCB Error Handling

**UTILITY SKILL**

Result-based error handling and logging discipline for the MCB Rust workspace.

## USE FOR

- Writing or reviewing fallible code paths.
- Choosing between `?`, `.context()`, and explicit error construction.

## DO NOT USE FOR

- Questions unrelated to MCB error handling.
- Generic Rust error handling outside MCB.

## Critical rules

- No `unwrap()`, `expect()`, `panic!()`, `todo!()`, or `unimplemented!()` in production code.
- Use `?` for propagation.
- Construct errors via factory methods (`Error::io`, `Error::embedding`, etc.), never raw variants.
- Use `tracing` for logs; no `println!`/`eprintln!` in production.

## Good examples

### Factory method + ? propagation

```rust
use mcb_domain::Error;
use mcb_infrastructure::error_ext::ErrorContext;

async fn embed_query(provider: &dyn EmbeddingProvider, text: &str) -> Result<Embedding> {
    provider.embed(text).await.context("embedding user query")
}
```

### Return typed error

```rust
use mcb_domain::Error;

if response.status().is_client_error() {
    return Err(Error::embedding("OpenAI API returned 429"));
}
```

### Logging with tracing

```rust
use tracing::{info, warn};

info!(user_id = %user_id, "session.started");
warn!(attempt = retry, "provider.timeout");
```

## Bad examples

### Unwrap in production

```rust
// WRONG
let result = provider.embed(text).await.unwrap();
```

### Raw variant construction

```rust
// WRONG
return Err(Error::ProviderError { message: "...".into() });
```

### Println in production

```rust
// WRONG
println!("debug: {:?}", value);
```

### Bare except equivalent

```rust
// WRONG
let value = match parse(input) {
    Ok(v) => v,
    Err(_) => 0, // swallows error
};
```

## Context enrichment

Use `ErrorContext::context` to add semantic labels as errors propagate:

```rust
let config = loader.load(path).await.context("loading development config")?;
```

## When to use each pattern

| Situation | Pattern |
|-----------|---------|
| Same error type | `?` |
| Need more context | `.context("...")?` |
| New semantic error | `Error::<variant>("...")` |
| Infallible option | `ok_or_else`/`ok_or` |
| Recovery is local | `match` + explicit handling |

## Verification

```bash
make check WHAT=lint      # clippy lints
make check WHAT=guard     # banned-pattern scanner
```

## References

- `mcb-domain/src/error/mod.rs` — `Error` enum and factory methods.
- `mcb-infrastructure/src/error_ext.rs` — `ErrorContext` trait.
- `docs/adr/019-error-handling-strategy.md` — full strategy.
