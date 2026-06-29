//! HTTP header extraction utilities for workspace provenance.
//!
//! **Documentation**: [docs/modules/server.md](../../../docs/modules/server.md)
//!
//! Provides utilities for extracting and mapping custom HTTP headers to
//! execution context overrides for workspace provenance enforcement, plus a
//! Tower layer that promotes the execution-flow header into a typed extension
//! so the MCP core stays free of Axum request types.

use std::collections::HashMap;
use std::task::{Context, Poll};

use axum::body::Body;
use axum::http::{HeaderMap, Request};
use mcb_utils::constants::headers::PROVENANCE_HEADER_MAPPINGS;
use mcb_utils::constants::protocol::HTTP_HEADER_EXECUTION_FLOW;
use tower::{Layer, Service};

/// Typed extension carrying an execution-flow header override.
///
/// Inserted by [`ExecutionFlowLayer`] and consumed by [`McpServer::call_tool`]
/// so the MCP core does not depend on Axum request parts.
#[derive(Clone, Debug)]
pub struct ExecutionFlowOverride(pub String);

/// Extract a single header value, trimming whitespace.
pub fn extract_override(headers: &HeaderMap, header_name: &str) -> Option<String> {
    headers
        .get(header_name)
        .and_then(|value| value.to_str().ok())
        .map(str::trim)
        .filter(|value| !value.is_empty())
        .map(ToOwned::to_owned)
}

/// Build a `HashMap` of header overrides from HTTP headers.
///
/// Maps custom headers to their corresponding context keys using the
/// centralized `PROVENANCE_HEADER_MAPPINGS` table plus execution flow.
#[must_use]
pub fn build_overrides(headers: &HeaderMap) -> HashMap<String, String> {
    let mut overrides = HashMap::new();

    for &(header_name, key) in PROVENANCE_HEADER_MAPPINGS {
        if let Some(value) = extract_override(headers, header_name) {
            overrides.insert(key.to_owned(), value);
        }
    }

    // Execution flow is transport-level, not provenance, but still overridden via header.
    if let Some(value) = extract_override(headers, HTTP_HEADER_EXECUTION_FLOW) {
        overrides.insert("execution_flow".to_owned(), value);
    }

    overrides
}

/// Tower middleware that promotes the execution-flow header into a typed
/// [`ExecutionFlowOverride`] extension.
#[derive(Clone, Debug, Default)]
pub struct ExecutionFlowLayer;

impl<S> Layer<S> for ExecutionFlowLayer {
    type Service = ExecutionFlowMiddleware<S>;

    fn layer(&self, inner: S) -> Self::Service {
        ExecutionFlowMiddleware { inner }
    }
}

/// Tower service that inserts [`ExecutionFlowOverride`] before delegating.
#[derive(Clone, Debug)]
pub struct ExecutionFlowMiddleware<S> {
    inner: S,
}

impl<S> Service<Request<Body>> for ExecutionFlowMiddleware<S>
where
    S: Service<Request<Body>>,
{
    type Response = S::Response;
    type Error = S::Error;
    type Future = S::Future;

    fn poll_ready(&mut self, cx: &mut Context<'_>) -> Poll<Result<(), Self::Error>> {
        self.inner.poll_ready(cx)
    }

    fn call(&mut self, mut req: Request<Body>) -> Self::Future {
        if let Some(value) = extract_override(req.headers(), HTTP_HEADER_EXECUTION_FLOW) {
            req.extensions_mut().insert(ExecutionFlowOverride(value));
        }
        self.inner.call(req)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use axum::body::Body;
    use axum::http::{Request, Response, StatusCode};

    #[derive(Clone)]
    struct CaptureService;

    impl Service<Request<Body>> for CaptureService {
        type Response = Response<Body>;
        type Error = axum::http::Error;
        type Future = std::future::Ready<Result<Self::Response, Self::Error>>;

        fn poll_ready(&mut self, _cx: &mut Context<'_>) -> Poll<Result<(), Self::Error>> {
            Poll::Ready(Ok(()))
        }

        fn call(&mut self, req: Request<Body>) -> Self::Future {
            let status = if req.extensions().get::<ExecutionFlowOverride>().is_some() {
                StatusCode::OK
            } else {
                StatusCode::NOT_FOUND
            };
            std::future::ready(Response::builder().status(status).body(Body::empty()))
        }
    }

    #[tokio::test]
    async fn execution_flow_layer_injects_typed_override() -> Result<(), Box<dyn std::error::Error>>
    {
        let mut service = ExecutionFlowLayer.layer(CaptureService);
        let req = Request::builder()
            .header(HTTP_HEADER_EXECUTION_FLOW, "hybrid")
            .body(Body::empty())?;
        let res = service.call(req).await?;
        assert_eq!(res.status(), StatusCode::OK);
        Ok(())
    }

    #[tokio::test]
    async fn execution_flow_layer_skips_missing_header() -> Result<(), Box<dyn std::error::Error>> {
        let mut service = ExecutionFlowLayer.layer(CaptureService);
        let req = Request::builder().body(Body::empty())?;
        let res = service.call(req).await?;
        assert_eq!(res.status(), StatusCode::NOT_FOUND);
        Ok(())
    }
}
