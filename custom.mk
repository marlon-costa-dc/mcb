# MCB private handlers for the FLEXT-generated Make surface.
# Public verbs and environment ownership remain in the generated Makefile.
#
# SCOPE RULE: a handler here exists only for what the generated Makefile does
# NOT already own. The dispatcher REPLACES the builtin when a `_custom_<verb>_
# <what>` target exists, so defining one for a verb the owner already
# implements silently disables the official gate. Everything Python — ruff
# format, ruff check, mypy/pyrefly/pyright, pytest — is owned by
# `_builtin_fmt_*`, `_builtin_fix_*`, `_builtin_check_all` and
# `_builtin_test_*`, and is therefore NEVER restated here. What remains is the
# Rust toolchain, which the FLEXT surface does not cover.

post-setup:
	@# Hook installation is NOT done here. codegen delegates it to
	@# `pre-commit install` so exactly one shim exists; copying a second script
	@# over .git/hooks made hook behaviour depend on whichever ran last.
	@# Why (mcb-o96i.19): CI runners need sccache installed before any cargo
	@# invocation because .cargo/config.toml sets rustc-wrapper = "sccache".
	@# The setup-ci.sh script installs sccache when not present. On local
	@# machines where sccache is already installed this is a no-op.
	@if [ "$$CI" = "Y" ] && [ -f .github/setup-ci.sh ]; then \
		bash .github/setup-ci.sh; \
	fi

_custom_build_artifacts:
	@if [ "$(RELEASE)" = "1" ]; then \
		bash scripts/lib/mcb.sh run cargo build --release; \
	else \
		bash scripts/lib/mcb.sh run cargo build; \
	fi

# Rust test selectors. `all`/`full` stay with the builtin so the FLEXT pytest
# entry keeps owning the Python suite; these are additional WHATs only.
_custom_test_unit:
	@if cargo nextest --version >/dev/null 2>&1; then \
		MCB_MODEL_ID=test-model bash scripts/lib/mcb.sh run cargo nextest run --workspace --test unit; \
	else \
		MCB_MODEL_ID=test-model bash scripts/lib/mcb.sh run cargo test --workspace --test unit; \
	fi

_custom_test_integration:
	@MCB_MODEL_ID=test-model bash scripts/lib/mcb.sh run cargo test --workspace --test '*integration*'

_custom_test_doc:
	@bash scripts/lib/mcb.sh run cargo test --workspace --doc

_custom_test_golden:
	@MCB_MODEL_ID=test-model bash scripts/lib/mcb.sh run cargo test -p mcb-server --test e2e "$(if $(strip $(MATCH)),$(MATCH),golden)"

_custom_test_rust:
	@if cargo nextest --version >/dev/null 2>&1; then \
		MCB_MODEL_ID=test-model bash scripts/lib/mcb.sh run cargo nextest run --workspace; \
	else \
		MCB_MODEL_ID=test-model bash scripts/lib/mcb.sh run cargo test --workspace --all-targets; \
	fi

# Rust-only check selectors. `all` stays with the builtin so `make check`
# keeps running the owner's declared CHECK_GATES under its own CI ternary.
_custom_check_lint:
	@bash scripts/lib/mcb.sh run cargo fmt --all -- --check
	@bash scripts/lib/mcb.sh run cargo clippy --all-targets -- -D warnings

_custom_check_validate:
	@bash scripts/lib/mcb.sh validate $(if $(filter 1,$(QUICK)),quick,full)

_custom_check_guard:
	@bash scripts/lib/mcb.sh guard

_custom_check_gitops:
	@$(UV_RUN) python scripts/check/gitops.py


_custom_check_audit:
	@bash scripts/lib/mcb.sh run cargo audit

<<<<<<< HEAD
_custom_check_all:
	@UV_CACHE_DIR=.cache/uv uv run --no-sync ruff check scripts
	@UV_CACHE_DIR=.cache/uv MYPYPATH=scripts uv run --no-sync mypy scripts/lib
	@UV_CACHE_DIR=.cache/uv uv run --no-sync pytest -m 'not slow' scripts/lib/tests
	@bash scripts/lib/mcb.sh run cargo fmt --all -- --check
	@bash scripts/lib/mcb.sh run cargo clippy --all-targets -- -D warnings
	@MCB_MODEL_ID=test-model bash scripts/lib/mcb.sh run cargo test --workspace --all-targets
	@bash scripts/lib/mcb.sh validate quick
	@bash scripts/lib/mcb.sh guard

_custom_run_mcb-hooks:
	$(call _require_apply)
	@$(MAKE) --no-print-directory post-setup

# CI is ternary (flext-infra config/codegen.yaml, RULING 1): CI=Y omits the
# gates the CI workflows own (lint/format/pyrefly/markdown) and revokes pytest;
# CI=N runs the full suite with coverage and keeps every blocking gate.
# pre-commit is the fast tier, so it declares CI=Y. pre-push is the complete
# local gate before the work leaves this machine, so it declares CI=N. The
# token is stated per command because each one is its own process.
_custom_run_mcb-hook-pre-commit:
	@CI=Y bash scripts/lib/mcb.sh guard --staged
	@CI=Y UV_CACHE_DIR=.cache/uv uv run --no-sync ruff check scripts
	@CI=Y UV_CACHE_DIR=.cache/uv uv run --no-sync pytest -m 'not slow' scripts/lib/tests
	@CI=Y bash scripts/lib/mcb.sh run cargo fmt --all -- --check
	@CI=Y bash scripts/lib/mcb.sh run cargo clippy --workspace -- -D warnings

_custom_run_mcb-hook-pre-push:
	@CI=N UV_CACHE_DIR=.cache/uv uv run --no-sync ruff check scripts
	@CI=N UV_CACHE_DIR=.cache/uv MYPYPATH=scripts uv run --no-sync mypy scripts/lib
	@CI=N UV_CACHE_DIR=.cache/uv uv run --no-sync pytest -m 'not slow' scripts/lib/tests
	@CI=N bash scripts/lib/mcb.sh run cargo fmt --all -- --check
	@CI=N bash scripts/lib/mcb.sh run cargo clippy --all-targets -- -D warnings
	@CI=N MCB_MODEL_ID=test-model bash scripts/lib/mcb.sh run cargo test --workspace --all-targets
	@CI=N bash scripts/lib/mcb.sh run cargo test --workspace --doc
	@CI=N bash scripts/lib/mcb.sh validate quick
	@CI=N bash scripts/lib/mcb.sh guard

=======
>>>>>>> origin/develop
_custom_gen_agent-pointers:
	@if [ "$(CHECK)" != "1" ] && [ "$(APPLY)" != "Y" ]; then printf 'ERROR: this action requires APPLY=Y\n' >&2; exit 2; fi
	@$(UV_RUN) python scripts/lib/agent_pointers.py $(if $(filter 1,$(CHECK)),--check,)
