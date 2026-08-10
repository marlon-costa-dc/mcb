# MCB private handlers for the FLEXT-generated Make surface.
# Public verbs and environment ownership remain in the generated Makefile.

post-setup:
	@hooks_dir=$$(git rev-parse --git-path hooks); \
		cp scripts/hooks/pre-commit scripts/hooks/pre-push "$$hooks_dir/"; \
		chmod +x "$$hooks_dir/pre-commit" "$$hooks_dir/pre-push"
	@printf '%s\n' 'MCB hooks installed'

_custom_build_artifacts:
	@if [ "$(RELEASE)" = "1" ]; then \
		bash scripts/lib/mcb.sh run cargo build --release; \
	else \
		bash scripts/lib/mcb.sh run cargo build; \
	fi

_custom_test_all:
	@if cargo nextest --version >/dev/null 2>&1; then \
		MCB_MODEL_ID=test-model bash scripts/lib/mcb.sh run cargo nextest run --workspace; \
	else \
		MCB_MODEL_ID=test-model bash scripts/lib/mcb.sh run cargo test --workspace --all-targets; \
	fi

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

_custom_fmt_check:
	@bash scripts/lib/mcb.sh run cargo fmt --all -- --check
	@UV_CACHE_DIR=.cache/uv uv run --no-sync ruff format --check scripts

_custom_fmt_all:
	$(call _require_apply)
	@bash scripts/lib/mcb.sh run cargo fmt --all
	@UV_CACHE_DIR=.cache/uv uv run --no-sync ruff format scripts

_custom_fmt_apply: _custom_fmt_all

_custom_fix_check:
	@UV_CACHE_DIR=.cache/uv uv run --no-sync ruff check scripts

_custom_fix_all:
	$(call _require_apply)
	@UV_CACHE_DIR=.cache/uv uv run --no-sync ruff check --fix scripts

_custom_fix_apply: _custom_fix_all

_custom_check_lint:
	@bash scripts/lib/mcb.sh run cargo fmt --all -- --check
	@bash scripts/lib/mcb.sh run cargo clippy --all-targets -- -D warnings

_custom_check_python:
	@UV_CACHE_DIR=.cache/uv uv run --no-sync ruff check scripts
	@UV_CACHE_DIR=.cache/uv MYPYPATH=scripts uv run --no-sync mypy scripts/lib
	@UV_CACHE_DIR=.cache/uv uv run --no-sync pytest -m 'not slow' scripts/lib/tests

_custom_check_validate:
	@bash scripts/lib/mcb.sh validate $(if $(filter 1,$(QUICK)),quick,full)

_custom_check_guard:
	@bash scripts/lib/mcb.sh guard

_custom_check_gitops:
	@UV_CACHE_DIR=.cache/uv uv run --no-sync python scripts/check/gitops.py

_custom_check_surface:
	@UV_CACHE_DIR=.cache/uv uv run --no-sync python scripts/check/surface.py

_custom_check_audit:
	@bash scripts/lib/mcb.sh run cargo audit

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

_custom_run_mcb-hook-pre-commit:
	@bash scripts/lib/mcb.sh guard --staged
	@UV_CACHE_DIR=.cache/uv uv run --no-sync ruff check scripts
	@UV_CACHE_DIR=.cache/uv uv run --no-sync pytest -m 'not slow' scripts/lib/tests
	@bash scripts/lib/mcb.sh run cargo fmt --all -- --check
	@bash scripts/lib/mcb.sh run cargo clippy --workspace -- -D warnings

_custom_run_mcb-hook-pre-push:
	@UV_CACHE_DIR=.cache/uv uv run --no-sync ruff check scripts
	@UV_CACHE_DIR=.cache/uv MYPYPATH=scripts uv run --no-sync mypy scripts/lib
	@UV_CACHE_DIR=.cache/uv uv run --no-sync pytest -m 'not slow' scripts/lib/tests
	@bash scripts/lib/mcb.sh run cargo fmt --all -- --check
	@bash scripts/lib/mcb.sh run cargo clippy --all-targets -- -D warnings
	@MCB_MODEL_ID=test-model bash scripts/lib/mcb.sh run cargo test --workspace --all-targets
	@bash scripts/lib/mcb.sh run cargo test --workspace --doc
	@bash scripts/lib/mcb.sh validate quick
	@bash scripts/lib/mcb.sh guard

_custom_gen_agent-pointers:
	@if [ "$(CHECK)" != "1" ] && [ "$(APPLY)" != "Y" ]; then printf 'ERROR: this action requires APPLY=Y\n' >&2; exit 2; fi
	@UV_CACHE_DIR=.cache/uv uv run --no-sync python scripts/lib/agent_pointers.py $(if $(filter 1,$(CHECK)),--check,)

_custom_status_done-check:
	@base=$$(git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null || printf '%s\n' origin/main); \
	files=$$(git diff --name-only --diff-filter=d "$$base"...HEAD -- '*.py'); \
	if [ -z "$$files" ]; then \
		printf '%s\n' 'done-check: no committed Python changes'; \
	else \
		printf '%s\n' "$$files" | xargs -r ruff check --quiet; \
	fi
