use mcb_domain::utils::tests::git_helpers::run_git;

use tempfile::TempDir;

use mcb_domain::ports::validation::ValidationConfig;
use mcb_validate::run_context::{FileInventorySource, ValidationRunContext};
use rstest::rstest;

#[rstest]
fn walkdir_inventory_respects_exclude_patterns() {
    let temp = TempDir::new().expect("tempdir");
    let root = temp.path();

    std::fs::create_dir_all(root.join("src")).expect("create src");
    std::fs::create_dir_all(root.join("target/generated")).expect("create target");
    std::fs::write(root.join("src/lib.rs"), "pub fn ok() {}\n").expect("write src");
    std::fs::write(root.join("target/generated/out.rs"), "pub fn skip() {}\n")
        .expect("write target");

    let config = ValidationConfig::new(root).with_exclude_pattern("target/");
    let context = ValidationRunContext::build(&config).expect("context");

    assert_eq!(
        context.file_inventory_source(),
        FileInventorySource::WalkDir
    );
    assert!(
        context
            .file_inventory()
            .iter()
            .any(|entry| entry.relative_path == std::path::Path::new("src/lib.rs"))
    );
    assert!(context.file_inventory().iter().all(|entry| {
        entry
            .relative_path
            .to_str()
            .is_none_or(|path| !path.contains("target/"))
    }));
}

#[rstest]
fn git_inventory_uses_git_source_when_repository_exists() {
    let temp = TempDir::new().expect("tempdir");
    let root = temp.path();

    // Route through the shared helper: it clears the inherited git environment,
    // so this repository is built here and not against the surrounding
    // repository when the suite runs inside a git hook.
    run_git(root, &["init"]).expect("run git init");

    std::fs::create_dir_all(root.join("src")).expect("create src");
    std::fs::write(root.join("src/lib.rs"), "pub fn ok() {}\n").expect("write src");

    run_git(root, &["add", "src/lib.rs"]).expect("run git add");

    let config = ValidationConfig::new(root);
    let context = ValidationRunContext::build(&config).expect("context");

    assert_eq!(context.file_inventory_source(), FileInventorySource::Git);
    assert!(
        context
            .file_inventory()
            .iter()
            .any(|entry| entry.relative_path == std::path::Path::new("src/lib.rs"))
    );
}
