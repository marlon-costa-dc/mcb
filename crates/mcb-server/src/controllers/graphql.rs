//! # CA Exception: Seaography GraphQL
//!
//! This controller is a declared Clean Architecture exception.
//! Seaography auto-generates GraphQL schema from `SeaORM` entities,
//! requiring direct `DatabaseConnection` access via `ctx.db`.
//! See docs/architecture/ARCHITECTURE.md for rationale.
//!
//! GraphQL playground and handler endpoints for Seaography auto-API.

use async_graphql::{
    dynamic::Schema,
    http::{GraphQLPlaygroundConfig, playground_source},
};
use async_graphql_axum::GraphQLRequest;
use axum::{extract::Extension, http::HeaderMap};
use loco_rs::prelude::*;
use seaography::async_graphql;

use crate::state::McbState;

/// Environment variable owning the GraphQL playground auth-header marker.
///
/// The playground page must emit an auth-header slot that its bootstrap script
/// replaces with the operator key held in browser `localStorage`. That marker
/// is deployment-owned configuration: it is read from the environment at
/// request time, never embedded in the binary (CWE-798), and constrained to a
/// safe token so it cannot break the generated page or smuggle markup.
const PLAYGROUND_KEY_MARKER_ENV: &str = "MCB_GRAPHQL_PLAYGROUND_KEY_MARKER";

/// Playground deployment configuration failures.
#[derive(Debug, thiserror::Error)]
pub enum PlaygroundConfigError {
    /// The marker environment variable is absent or empty.
    #[error(
        "environment variable {env} is not set; the GraphQL playground refuses to serve without \
         its deployment-owned auth-header marker"
    )]
    Missing {
        /// Name of the missing environment variable.
        env: &'static str,
    },
    /// The marker holds characters that cannot appear in the generated page.
    #[error(
        "environment variable {env} holds an invalid marker (only [A-Za-z0-9_-], at most 64 \
         characters): {value:?}"
    )]
    Invalid {
        /// Name of the offending environment variable.
        env: &'static str,
        /// The rejected value.
        value: String,
    },
}

/// Typed deployment configuration for the playground auth header.
///
/// Resolved from `MCB_GRAPHQL_PLAYGROUND_KEY_MARKER` (the marker written into
/// the page and immediately replaced by the bootstrap script) and from the
/// deployment's configured API-key header name, so the page always requests
/// the header this server actually authenticates.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PlaygroundAuthConfig {
    header_name: String,
    marker: String,
}

impl PlaygroundAuthConfig {
    /// Resolve the marker from its raw deployment value and the runtime
    /// settings that own the API-key header name.
    ///
    /// # Errors
    /// Fails loud when the marker is absent, empty, or not a safe page token.
    pub fn from_marker(
        marker: &str,
        settings: Option<&serde_json::Value>,
    ) -> Result<Self, PlaygroundConfigError> {
        let trimmed = marker.trim();
        if trimmed.is_empty() {
            return Err(PlaygroundConfigError::Missing {
                env: PLAYGROUND_KEY_MARKER_ENV,
            });
        }
        let marker_ok = trimmed.len() <= 64
            && trimmed
                .bytes()
                .all(|b| b.is_ascii_alphanumeric() || b == b'_' || b == b'-');
        if !marker_ok {
            return Err(PlaygroundConfigError::Invalid {
                env: PLAYGROUND_KEY_MARKER_ENV,
                value: trimmed.to_owned(),
            });
        }
        Ok(Self {
            header_name: crate::auth::configured_api_key_header(settings),
            marker: trimmed.to_owned(),
        })
    }

    /// Resolve from the process environment; fail loud when absent.
    ///
    /// # Errors
    /// Propagates [`PlaygroundConfigError`] for missing or invalid markers.
    pub fn resolve(settings: Option<&serde_json::Value>) -> Result<Self, PlaygroundConfigError> {
        let raw = std::env::var(PLAYGROUND_KEY_MARKER_ENV).map_err(|_| {
            PlaygroundConfigError::Missing {
                env: PLAYGROUND_KEY_MARKER_ENV,
            }
        })?;
        Self::from_marker(&raw, settings)
    }

    /// The auth-header name the page will populate from `localStorage`.
    #[must_use]
    pub fn header_name(&self) -> &str {
        &self.header_name
    }
}

/// Render the playground HTML page for a resolved configuration.
///
/// The emitted page contains no auth marker value: the header slot is replaced
/// by a script expression that reads the operator key from `localStorage` in
/// the browser.
#[must_use]
pub fn render_playground_page(config: &PlaygroundAuthConfig) -> String {
    let header = config.header_name.as_str();
    let marker = config.marker.as_str();
    let playground_config = GraphQLPlaygroundConfig::new("/api/graphql")
        .with_header(header, marker);

    playground_source(playground_config).replace(
        &format!(r#""{header}":"{marker}""#),
        &format!(r#""{header}":`${{localStorage.getItem('api_key') || ''}}`"#),
    )
}

async fn graphql_playground(State(ctx): State<AppContext>) -> Result<Response> {
    let config = PlaygroundAuthConfig::resolve(ctx.config.settings.as_ref())
        .map_err(|e| loco_rs::Error::string(&format!("graphql playground disabled: {e}")))?;

    Ok(Response::new(render_playground_page(&config).into()))
}

async fn graphql_handler(
    Extension(state): Extension<McbState>,
    State(ctx): State<AppContext>,
    headers: HeaderMap,
    gql_req: GraphQLRequest,
) -> std::result::Result<async_graphql_axum::GraphQLResponse, (axum::http::StatusCode, &'static str)>
{
    crate::auth::authorize_admin_api_key(
        state.auth_repo.as_ref(),
        &headers,
        ctx.config.settings.as_ref(),
    )
    .await
    .map_err(|_| (axum::http::StatusCode::UNAUTHORIZED, "Unauthorized"))?;

    let mut gql_req = gql_req.into_inner();
    gql_req = gql_req.data(seaography::UserContext { user_id: 0 });

    let schema: Schema = ctx.shared_store.get().ok_or((
        axum::http::StatusCode::INTERNAL_SERVER_ERROR,
        "GraphQL not setup",
    ))?;
    let res: async_graphql_axum::GraphQLResponse = schema.execute(gql_req).await.into();

    Ok(res)
}

/// Registers GraphQL playground (`GET /graphql`) and handler (`POST /graphql`) routes.
pub fn routes() -> Routes {
    Routes::new()
        .prefix("graphql")
        .add("/", get(graphql_playground))
        .add("/", post(graphql_handler))
}
