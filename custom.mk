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

pre-check:
	@bash scripts/lib/mcb.sh conflict-markers

# Why (mcb-da36): the work saga pushes via GitPython, which inherits the
# recipe environment. Make exports command-line variables (WHAT=land APPLY=Y)
# into every recipe, so without a scrub the pre-push hooks spawned by that
# push re-parse the tokens as their own WHAT and abort with
# 'unsupported gen WHAT=land' / 'check does not accept APPLY'. The scrub
# runs the SAME builtin saga command from a shell with the leaked dispatch
# tokens and make flag carriers removed, so GitPython and every hook it
# triggers see a clean invocation environment. Verified: env WHAT=land
# pre-commit run flext-pre-push-gen fails; env -u WHAT -u APPLY passes.
_custom_work_start:
	@unset WHAT APPLY MAKEFILES GNUMAKEFLAGS MAKEFLAGS MAKELEVEL MAKEOVERRIDES MFLAGS; \
		$(MAKE) --no-print-directory -f "$(SELF_MAKEFILE)" _builtin_work_start

_custom_work_land:
	@unset WHAT APPLY MAKEFILES GNUMAKEFLAGS MAKEFLAGS MAKELEVEL MAKEOVERRIDES MFLAGS; \
		$(MAKE) --no-print-directory -f "$(SELF_MAKEFILE)" _builtin_work_land

_custom_work_finish:
	@unset WHAT APPLY MAKEFILES GNUMAKEFLAGS MAKEFLAGS MAKELEVEL MAKEOVERRIDES MFLAGS; \
		$(MAKE) --no-print-directory -f "$(SELF_MAKEFILE)" _builtin_work_finish

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
	@$(UV_RUN) python scripts/check/gitops.py run


_custom_check_audit:
	@bash scripts/lib/mcb.sh run cargo audit

_custom_gen_agent-pointers:
	@if [ "$(CHECK)" != "1" ] && [ "$(APPLY)" != "Y" ]; then printf 'ERROR: this action requires APPLY=Y\n' >&2; exit 2; fi
	@$(UV_RUN) python scripts/lib/agent_pointers.py $(if $(filter 1,$(CHECK)),--check,)
