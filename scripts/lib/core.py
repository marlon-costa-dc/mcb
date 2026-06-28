"""FLEXT-style core primitives for MCB Python tooling.

This module provides a local, dependency-light bridge that mirrors the
fundamental aliases and contracts used by the FLEXT workspace:

- ``Result[T]`` / ``Ok`` / ``Err`` — explicit fallible results.
- ``get_logger`` — structured logging via structlog.
- ``BaseMcbSettings`` — Pydantic ``BaseSettings`` with ``MCB_`` env prefix.

It intentionally does **not** depend on ``flext_core`` so that MCB remains
self-contained, but it keeps the same shape so cross-project alignment is
straightforward.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

import structlog
from pydantic_settings import BaseSettings, SettingsConfigDict

T = TypeVar("T")
U = TypeVar("U")


class _Ok[T]:
    __slots__ = ("value",)

    def __init__(self, value: T) -> None:
        self.value = value


class _Err:
    __slots__ = ("error",)

    def __init__(self, error: Exception) -> None:
        self.error = error


class Result[T]:
    """Explicit fallible result container matching FLEXT ``r[T]`` semantics.

    Use :func:`Ok` and :func:`Err` to construct values. Prefer ``is_ok`` /
    ``is_err`` checks at boundaries, and propagate errors with ``map`` /
    ``flat_map`` rather than raising exceptions for expected failures.
    """

    __slots__ = ("_inner",)

    def __init__(self, inner: _Ok[T] | _Err) -> None:
        self._inner = inner

    @property
    def is_ok(self) -> bool:
        return isinstance(self._inner, _Ok)

    @property
    def is_err(self) -> bool:
        return isinstance(self._inner, _Err)

    def unwrap(self) -> T:
        if isinstance(self._inner, _Err):
            raise self._inner.error
        return self._inner.value

    def unwrap_or(self, default: T) -> T:
        if isinstance(self._inner, _Err):
            return default
        return self._inner.value

    def unwrap_or_else(self, op: Callable[[Exception], T]) -> T:
        if isinstance(self._inner, _Err):
            return op(self._inner.error)
        return self._inner.value

    def map(self, op: Callable[[T], U]) -> Result[U]:
        if isinstance(self._inner, _Err):
            return Result(_Err(self._inner.error))
        return Result(_Ok(op(self._inner.value)))

    def flat_map(self, op: Callable[[T], Result[U]]) -> Result[U]:
        if isinstance(self._inner, _Err):
            return Result(_Err(self._inner.error))
        return op(self._inner.value)

    @property
    def error(self) -> Exception | None:
        if isinstance(self._inner, _Err):
            return self._inner.error
        return None


def Ok[T](value: T) -> Result[T]:
    """Create a successful result."""
    return Result(_Ok(value))


def Err[T](error: Exception) -> Result[T]:
    """Create a failed result."""
    return Result(_Err(error))


def configure_logging(json_format: bool = False) -> None:
    """Configure structlog for MCB scripts.

    Call once at each CLI entrypoint. In normal dev mode logs are rendered as
    plain key=value lines; set ``json_format=True`` (or ``MCB_LOG_JSON=1``) for
    JSON output suitable for CI aggregation.
    """
    import logging
    import os

    use_json = json_format or os.environ.get("MCB_LOG_JSON", "").lower() in ("1", "true", "yes")

    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.ExtraAdder(),
    ]

    formatter = (
        structlog.processors.JSONRenderer()
        if use_json
        else structlog.dev.ConsoleRenderer()
    )

    structlog.configure(
        processors=shared_processors + [structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    handler = logging.StreamHandler()
    handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            processor=formatter,
            foreign_pre_chain=shared_processors,
        )
    )

    root = logging.getLogger()
    root.handlers[:] = [handler]
    root.setLevel(logging.INFO)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Fetch a structured logger for the given module name."""
    import typing

    return typing.cast(structlog.stdlib.BoundLogger, structlog.get_logger(name))


class BaseMcbSettings(BaseSettings):
    """Base settings for MCB scripts.

    Environment variables are read with the ``MCB_`` prefix, e.g.
    ``MCB_LOG_LEVEL`` maps to ``log_level``.
    """

    model_config = SettingsConfigDict(env_prefix="MCB_", extra="ignore")


__all__ = [
    "BaseMcbSettings",
    "Err",
    "Ok",
    "Result",
    "get_logger",
]
