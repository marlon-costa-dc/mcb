//! Pattern-registry rules-directory containment tests (path-traversal cure).
//!
//! `MCB_RULES_DIR` is untrusted boundary input for a filesystem read: the
//! override is accepted only when the path resolves, after symlink
//! canonicalization, inside a trust root (the crate manifest directory or its
//! owning workspace root). Escapes are rejected, never normalized.

use std::path::PathBuf;

use mcb_domain::utils::tests::guards::EnvVarGuard;
use serial_test::serial;
use mcb_validate::pattern_registry::default_rules_dir;

const RULES_DIR_ENV: &str = "MCB_RULES_DIR";

fn manifest_dir() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
}

#[test]
#[serial]
fn contained_override_is_accepted_and_canonicalized() {
    let temp = tempfile::tempdir_in(manifest_dir()).expect("temp dir inside manifest root");
    let rules = temp.path().join("rules");
    std::fs::create_dir_all(&rules).expect("create rules dir");

    let _guard = EnvVarGuard::set(RULES_DIR_ENV, rules.to_str().expect("utf8 path"));
    let resolved = default_rules_dir();

    assert!(
        resolved.starts_with(manifest_dir().canonicalize().expect("manifest canonical")),
        "override {resolved:?} must resolve inside the manifest root"
    );
    assert_eq!(
        resolved.file_name().and_then(|name| name.to_str()),
        Some("rules")
    );
}

/// ATTACK: an absolute path outside every trust root must be rejected — the
/// resolution must fall back to the crate's own rules directory instead of
/// reading rules from an attacker-chosen location.
#[test]
#[serial]
fn absolute_escape_is_rejected() {
    let outside = tempfile::tempdir().expect("temp dir outside the workspace");
    let rules = outside.path().join("rules");
    std::fs::create_dir_all(&rules).expect("create outside rules dir");

    let _guard = EnvVarGuard::set(RULES_DIR_ENV, rules.to_str().expect("utf8 path"));
    let resolved = default_rules_dir();

    assert_ne!(resolved, rules);
    assert!(
        !resolved.starts_with(outside.path()),
        "override {resolved:?} escaped the trust roots"
    );
    assert_eq!(resolved, manifest_dir().join("rules"));
}

/// ATTACK: parent-directory components must be rejected structurally, even
/// when the target of the traversal exists.
#[test]
#[serial]
fn parent_directory_components_are_rejected() {
    let sneaky = manifest_dir()
        .join("target")
        .join("..")
        .join("..")
        .join("crates");

    let _guard = EnvVarGuard::set(RULES_DIR_ENV, sneaky.to_str().expect("utf8 path"));
    let resolved = default_rules_dir();

    assert_eq!(
        resolved,
        manifest_dir().join("rules"),
        "traversal override must fall back to the crate rules directory"
    );
}

/// ATTACK: a symlink placed inside a trust root but pointing outside it must
/// be rejected after canonicalization (symlink escape).
#[test]
#[serial]
#[cfg(unix)]
fn symlink_escape_is_rejected() {
    use std::os::unix::fs::symlink;

    let outside = tempfile::tempdir().expect("outside temp dir");
    let outside_rules = outside.path().join("rules");
    std::fs::create_dir_all(&outside_rules).expect("create outside rules dir");

    let link = manifest_dir().join("target").join("mcb_rules_escape_link");
    std::fs::create_dir_all(link.parent().expect("link parent")).expect("create link parent");
    let _ = std::fs::remove_file(&link);
    symlink(&outside_rules, &link).expect("create escape symlink");

    let result;
    {
        let _guard = EnvVarGuard::set(RULES_DIR_ENV, link.to_str().expect("utf8 path"));
        result = default_rules_dir();
    }
    let _ = std::fs::remove_file(&link);

    assert_eq!(
        result,
        manifest_dir().join("rules"),
        "symlink escape must fall back to the crate rules directory"
    );
}

/// With no override set, resolution is unchanged: the crate's own rules
/// directory.
#[test]
#[serial]
fn absent_override_keeps_manifest_rules() {
    EnvVarGuard::remove(&[RULES_DIR_ENV]);
    assert_eq!(default_rules_dir(), manifest_dir().join("rules"));
}
