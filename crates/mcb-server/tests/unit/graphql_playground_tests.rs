//! GraphQL playground auth-marker tests (CWE-798 cure).
//!
//! The playground page must never embed a credential-shaped literal: the
//! auth-header marker is deployment-owned (`MCB_GRAPHQL_PLAYGROUND_KEY_MARKER`),
//! validated at the boundary, and replaced in the rendered page by a
//! `localStorage` read on the client.

use mcb_server::controllers::graphql::{PlaygroundAuthConfig, PlaygroundConfigError};
use rstest::rstest;

#[rstest]
fn marker_resolves_into_typed_config() {
    let config = PlaygroundAuthConfig::from_marker("deploy-marker-01", None).expect("marker");
    assert_eq!(config.header_name(), "x-api-key");
}

#[rstest]
fn missing_marker_fails_loud() {
    let error = PlaygroundAuthConfig::from_marker("", None).expect_err("empty marker rejected");
    assert!(matches!(error, PlaygroundConfigError::Missing { .. }));
}

#[rstest]
#[case("   ")]
fn blank_marker_fails_loud(#[case] marker: &str) {
    let error = PlaygroundAuthConfig::from_marker(marker, None).expect_err("blank rejected");
    assert!(matches!(error, PlaygroundConfigError::Missing { .. }));
}

/// ATTACK: a marker carrying JSON-string breakers / markup must be rejected at
/// the boundary so it can never reach the generated page.
#[rstest]
#[case("auto\"key\"")]
#[case("auto'><script>")]
#[case("auto key with spaces")]
#[case("auto/key")]
fn hostile_marker_is_rejected(#[case] marker: &str) {
    let error = PlaygroundAuthConfig::from_marker(marker, None).expect_err("hostile marker");
    assert!(matches!(error, PlaygroundConfigError::Invalid { .. }));
}

/// ATTACK continuation: an oversized marker cannot be smuggled past the token
/// constraint either.
#[rstest]
fn oversized_marker_is_rejected() {
    let marker = "a".repeat(65);
    let error =
        PlaygroundAuthConfig::from_marker(&marker, None).expect_err("oversized marker rejected");
    assert!(matches!(error, PlaygroundConfigError::Invalid { .. }));
}

/// The rendered page carries the marker only inside the JSON slot that the
/// bootstrap script replaces; the emitted HTML must read the key from
/// `localStorage` and must not contain the marker value anywhere.
#[rstest]
fn rendered_page_never_embeds_the_marker() {
    let config =
        PlaygroundAuthConfig::from_marker("deploy-marker-01", None).expect("valid marker");
    let page = mcb_server::controllers::graphql::render_playground_page(&config);

    assert!(
        !page.contains("deploy-marker-01"),
        "playground page leaked the deployment marker"
    );
    assert!(
        page.contains("localStorage.getItem('api_key')"),
        "playground page must read the key from browser localStorage"
    );
    assert!(
        page.contains("\"x-api-key\":"),
        "playground page must populate the configured auth header"
    );
}
