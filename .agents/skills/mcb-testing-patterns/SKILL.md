---
name: mcb-testing-patterns
description: Test-driven development and test layout patterns for the MCB Rust workspace. Use when writing, reviewing, or debugging tests.
license: MIT
metadata:
  version: 1.0.0
---

# MCB Testing Patterns

**UTILITY SKILL**

TDD and test organization for the MCB Rust workspace.

## USE FOR

- Writing new tests, fixtures, or test helpers.
- Reviewing test quality and coverage.

## DO NOT USE FOR

- Questions unrelated to MCB testing.
- Generic Rust testing outside MCB.

## Critical rules

- Red-Green-Refactor: failing test first, then implementation.
- Integration tests live in `tests/` directory, not inline `#[cfg(test)]`.
- Use `rstest` for parameterized tests, `mockall` for mocks, `insta` for snapshots, `tempfile` for temp dirs.
- Force linkme registration in integration tests with `extern crate mcb_providers;`.

## Test layout

```text
crates/mcb-{name}/
└── tests/
    ├── lib.rs           # Test module root
    ├── unit.rs          # Unit test module
    ├── integration.rs   # Integration test module
    ├── unit/*_tests.rs  # Individual unit test files
    └── utils/           # Shared test helpers
```

## Good examples

### Unit test file

```rust
// crates/mcb-domain/tests/unit/value_objects_tests.rs
use mcb_domain::value_objects::ids::SessionId;

#[test]
fn session_id_parses_valid_uuid() {
    let id = SessionId::new();
    assert!(!id.to_string().is_empty());
}
```

### Parameterized test with rstest

```rust
use rstest::rstest;

#[rstest]
#[case("hello", 5)]
#[case("world", 5)]
fn length_is_correct(#[case] input: &str, #[case] expected: usize) {
    assert_eq!(input.len(), expected);
}
```

### Snapshot test with insta

```rust
use insta::assert_json_snapshot;

#[test]
fn serializes_config() {
    let config = Config::default();
    assert_json_snapshot!(config);
}
```

### Integration test with real providers

```rust
// Force linkme distributed-slice registration
extern crate mcb_providers;

use mcb_domain::ports::providers::EmbeddingProvider;
use mcb_infrastructure::di::bootstrap::init_app;

#[tokio::test]
async fn app_initializes_with_default_config() {
    let ctx = init_app(Config::test()).await.unwrap();
    assert!(ctx.embedding.list().len() > 0);
}
```

## Bad examples

### Unwrap in test assertion

```rust
// WRONG: even tests should assert meaningfully
let ctx = init_app(config).await.unwrap();
```

### Inline integration tests

```rust
// WRONG: keep integration tests in tests/
#[cfg(test)]
mod integration_tests { ... }
```

### Mocking the wrong layer

```rust
// WRONG: mock at the port boundary, not inside domain
mock!(DomainEntity, ...);
```

## Running tests

```bash
make test                          # full suite
make test SCOPE=unit               # unit tests only
make test SCOPE=integration        # integration tests
make test SCOPE=doc                # doctests
cargo test -p mcb-server --test unit -- my_test --nocapture
```

## Verification

```bash
make test SCOPE=unit
make test SCOPE=integration
```

## References

- `docs/developer/CONTRIBUTING.md` — testing guidelines.
- `docs/adr/020-testing-strategy-integration.md` — testing strategy.
