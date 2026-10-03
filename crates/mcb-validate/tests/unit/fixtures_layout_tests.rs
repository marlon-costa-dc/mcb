//! Fixture-tree layout invariant (command-injection taint cure).
//!
//! Validator inputs live exclusively in the owned `tests/fixtures/rust/`
//! root. Vendored third-party source trees under `tests/fixtures/` are a
//! defect: an abandoned vendored tool (`rustlings`) carrying process-spawn
//! sinks (`Command::new`) previously produced a cross-file command-injection
//! taint finding against this crate. This guard keeps the fixture surface
//! vendored-free.

use std::path::PathBuf;

fn fixtures_root() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("tests").join("fixtures")
}

/// The fixture surface contains only the owned `rust` fixture root: no
/// vendored third-party trees, no tool source, no process-spawn sinks.
#[test]
fn fixtures_root_holds_only_the_owned_rust_root() {
    let mut entries: Vec<String> = std::fs::read_dir(fixtures_root())
        .expect("read fixtures root")
        .map(|entry| entry.expect("fixture entry").file_name().to_string_lossy().into_owned())
        .collect();
    entries.sort();

    assert_eq!(
        entries, ["rust"],
        "tests/fixtures must contain only the owned 'rust' fixture root; vendored \
         third-party trees are forbidden (command-injection taint cure)"
    );
}

/// The owned fixture root must not carry process-spawn sinks of its own:
/// validator inputs are static sample code, not executable tool source.
#[test]
fn owned_fixture_root_carries_no_command_execution_sinks() {
    fn walk(dir: &std::path::Path, hits: &mut Vec<PathBuf>) {
        let Ok(entries) = std::fs::read_dir(dir) else {
            return;
        };
        for entry in entries.flatten() {
            let path = entry.path();
            if path.is_dir() {
                walk(&path, hits);
            } else if path.extension().is_some_and(|ext| ext == "rs") {
                let Ok(content) = std::fs::read_to_string(&path) else {
                    continue;
                };
                if content.contains("Command::new") || content.contains("std::process::Command") {
                    hits.push(path);
                }
            }
        }
    }

    let mut hits = Vec::new();
    walk(&fixtures_root().join("rust"), &mut hits);
    assert!(
        hits.is_empty(),
        "validator fixtures must not carry process-spawn sinks: {hits:?}"
    );
}
