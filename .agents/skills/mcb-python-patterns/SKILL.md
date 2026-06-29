---
name: mcb-python-patterns
description: FLEXT-aligned Python patterns for MCB scripts/. Use when writing, reviewing, or refactoring Python tooling under scripts/.
license: MIT
metadata:
  version: 1.0.0
---

# MCB Python Patterns

**Use this skill when writing, reviewing, or refactoring Python code under `scripts/` in the MCB repository.**

MCB Python tooling is built on [FLEXT](https://github.com/marlonsc/flext) primitives:
`FlextResult`, `FlextSettingsBase`, `FlextLogger`, and `FlextService`. The local
names and conventions are documented in `FLEXT_TO_MCB_MAPPING.md`.

## One-minute rules

- Return `r[T]` (`McbResult`) from business functions; never `print`/`sys.exit`.
- Use `BaseMcbSettings` / `BaseCommandSettings` / `McbSettings` for configuration.
- Get loggers with `get_logger(__name__)`; no `print()`.
- Keep one class per module; no god modules.
- Import order: `__future__` → stdlib → third-party → `lib.*` → `qlty.*` / `docs.py.*`.
- Run the four Python gates before claiming done:
  - `make check WHAT=python ACT=lint`
  - `make check WHAT=python ACT=test`
  - `make check WHAT=python ACT=guard`
  - or `make check WHAT=python ACT=all`

## Result containers

```python
from lib.core import r

def load_issues(path: Path) -> r[list[Issue]]:
    if not path.exists():
        return r[list[Issue]].fail(f"missing: {path}")
    return r[list[Issue]].ok(_parse(path))
```

Propagate failures at call sites:

```python
issues_result = load_issues(path)
if issues_result.failure:
    return issues_result
issues = issues_result.unwrap()
```

## Settings

For scripts invoked through `cosmos-command` (unprefixed env vars):

```python
from lib.core import BaseCommandSettings
from pydantic import Field

class MySettings(BaseCommandSettings):
    root: Path = Field(default=Path("."), description="Project root")
```

For library-style scripts that read `MCB_*` env vars:

```python
from lib.settings import McbSettings

settings = McbSettings()
report_file = settings.qlty_report_md
```

## Logging

```python
from lib.core import get_logger

logger = get_logger(__name__)
logger.info("processed", count=len(items))
```

## CLI wiring

```python
from lib.cli import create_app_with_common_params, register_result_command

def run(settings: MySettings) -> r[int]:
    ...

def main() -> None:
    app = create_app_with_common_params(name="my-cmd", help_text="...")
    register_result_command(
        app,
        name="run",
        help_text="...",
        model_cls=MySettings,
        handler=run,
    )
    app()
```

## Good vs bad

| Good | Bad |
|------|-----|
| `return r[int].fail("...")` | `print("..."); sys.exit(1)` |
| `settings.qlty_smells_sarif` | `Path("qlty.smells.sarif")` inline |
| `logger.info("done")` | `print("done")` |
| `result.unwrap()` in tests | `result.value` (does not exist) |
| One class/module | `core.py` with 5 unrelated classes |

## Verification

```bash
make check WHAT=python ACT=all
```

## References

- `FLEXT_TO_MCB_MAPPING.md`
- `scripts/lib/core.py`
- `scripts/lib/settings.py`
- `scripts/lib/cli.py`
