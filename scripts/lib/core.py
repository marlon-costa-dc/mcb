"""FLEXT-style core kernel for MCB Python tooling.

Copyright (c) 2025 MCB Contributors. All rights reserved.
SPDX-License-Identifier: MIT

This module provides a local, Pydantic-based kernel that mirrors the
fundamental aliases and contracts used by the FLEXT workspace:

- ``McbResult[T]`` (alias ``r``) — explicit fallible results with monadic helpers.
- ``BaseMcbSettings`` — Pydantic ``BaseSettings`` with singleton lifecycle.
- ``McbService`` (alias ``s``) — per-class singleton service base.
- ``McbLogger`` / ``get_logger`` — structured logging via structlog.

It intentionally does **not** depend on ``flext_core`` so that MCB remains
self-contained, but it keeps the same shape so cross-project alignment is
straightforward.
"""

from __future__ import annotations

import logging
import os
import threading
from collections.abc import Callable, Generator, Sequence
from contextlib import contextmanager
from pathlib import Path
from types import TracebackType
from typing import (
    Annotated,
    Any,
    ClassVar,
    Self,
    TypeVar,
    Unpack,
    overload,
)

import structlog
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr
from pydantic_settings import BaseSettings, SettingsConfigDict

from .constants import c

T = TypeVar("T")
U = TypeVar("U")


class McbResult[T](BaseModel):
    """Type-safe, Pydantic-based result container.

    Use :meth:`ok` and :meth:`fail` to construct values. Prefer ``is_ok`` /
    ``is_err`` checks at boundaries, and propagate errors with ``map`` /
    ``flat_map`` rather than raising exceptions for expected failures.
    """

    model_config: ClassVar[ConfigDict] = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        serialize_by_alias=True,
    )

    result_success: Annotated[bool, Field(alias="success")] = True
    result_error: Annotated[str | None, Field(alias="error")] = None
    result_error_code: Annotated[str | None, Field(alias="error_code")] = None

    _payload: T | None = PrivateAttr(default=None)
    _exception: BaseException | None = PrivateAttr(default=None)

    @property
    def success(self) -> bool:
        """Success flag."""
        return self.result_success

    @property
    def failure(self) -> bool:
        """Failure flag."""
        return not self.result_success

    @property
    def error(self) -> str | None:
        """Error message."""
        return self.result_error

    @property
    def error_code(self) -> str | None:
        """Error code."""
        return self.result_error_code

    @property
    def exception(self) -> BaseException | None:
        """Captured exception, if any."""
        return self._exception

    def __init__(
        self,
        *,
        value: T | None = None,
        error: str | None = None,
        error_code: str | None = None,
        success: bool = True,
        exception: BaseException | None = None,
    ) -> None:
        super().__init__(
            success=success,
            error=error,
            error_code=error_code,
        )
        if success:
            self._payload = value
        self._exception = exception

    def __repr__(self) -> str:
        if self.success:
            return f"r[T].ok({self.value!r})"
        return f"r[T].fail({self.error!r})"

    def __bool__(self) -> bool:
        return self.success

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        _exc_type: type[BaseException] | None,
        _exc_val: BaseException | None,
        _exc_tb: TracebackType | None,
    ) -> None:
        pass

    @overload
    def __or__(self, default: T) -> T: ...

    @overload
    def __or__[DefaultT](self, default: T | DefaultT) -> T | DefaultT: ...

    def __or__[DefaultT](self, default: T | DefaultT) -> T | DefaultT:
        """Return success value or ``default`` (syntactic sugar)."""
        return self.unwrap_or(default)

    @property
    def is_ok(self) -> bool:
        """True when the result is successful."""
        return self.success

    @property
    def is_err(self) -> bool:
        """True when the result is a failure."""
        return self.failure

    @property
    def value(self) -> T:
        """Success payload; raises on failure or missing payload."""
        if self.failure:
            msg = c.ERR_RESULT_CANNOT_ACCESS_VALUE.format(error=self.error)
            raise RuntimeError(msg)
        if self._payload is None:
            msg = "Successful result must have a non-None payload"
            raise ValueError(msg)
        return self._payload

    @classmethod
    def ok(cls, value: T) -> McbResult[T]:
        """Create a successful result wrapping ``value``."""
        return cls(value=value, success=True)

    @classmethod
    def fail(
        cls,
        error: str,
        *,
        error_code: str | None = None,
        exception: BaseException | None = None,
    ) -> McbResult[T]:
        """Create a failed result with message, optional code and exception."""
        return cls(
            error=error,
            error_code=error_code,
            success=False,
            exception=exception,
        )

    @classmethod
    def fail_op(cls, operation: str, exc: Exception | str | None = None) -> McbResult[T]:
        """Create a failure result for a named operation with optional exception."""
        if isinstance(exc, Exception):
            return cls.fail(f"{operation} failed: {exc}", exception=exc)
        if exc is None:
            return cls.fail(f"{operation} failed")
        return cls.fail(f"{operation} failed: {exc}")

    @classmethod
    def from_validation(
        cls,
        data: Any,
        model: type[BaseModel],
    ) -> McbResult[BaseModel]:
        """Create a result from Pydantic validation."""
        try:
            return cls.ok(model.model_validate(data))
        except c.EXC_VALIDATION_TYPE_VALUE as exc:
            return cls.fail(str(exc), exception=exc)

    @classmethod
    def accumulate_errors[ValueT](
        cls,
        *results: McbResult[ValueT],
    ) -> McbResult[Sequence[ValueT]]:
        """Collect successes or combine all errors."""
        successes: list[ValueT] = []
        errors: list[str] = []
        for result in results:
            if result.success:
                successes.append(result.value)
            else:
                errors.append(result.error or "Unknown error")
        if errors:
            return cls.fail("; ".join(errors))
        return cls.ok(successes)

    @staticmethod
    def safe[U, **PFunc](func: Callable[PFunc, U]) -> Callable[PFunc, McbResult[U]]:
        """Decorator: wrap ``func`` in ``McbResult`` and catch common exceptions."""

        def wrapper(*args: PFunc.args, **kwargs: PFunc.kwargs) -> McbResult[U]:
            try:
                return McbResult[U].ok(func(*args, **kwargs))
            except c.EXC_BROAD_RUNTIME as exc:
                return McbResult[U].fail(str(exc), exception=exc)

        return wrapper

    def map(self, op: Callable[[T], U]) -> McbResult[U]:
        """Transform success value; propagate failure unchanged."""
        if self.failure:
            return McbResult[U].fail(
                self.error or "",
                error_code=self.error_code,
                exception=self._exception,
            )
        try:
            return McbResult[U].ok(op(self.value))
        except Exception as exc:  # noqa: BLE001
            return McbResult[U].fail(str(exc), exception=exc)

    def flat_map(self, op: Callable[[T], McbResult[U]]) -> McbResult[U]:
        """Chain operations that themselves return ``McbResult``."""
        if self.failure:
            return McbResult[U].fail(
                self.error or "",
                error_code=self.error_code,
                exception=self._exception,
            )
        return op(self.value)

    def fold(
        self,
        on_failure: Callable[[str], U],
        on_success: Callable[[T], U],
    ) -> U:
        """Catamorphism: reduce result to a single value via callbacks."""
        if self.success:
            return on_success(self.value)
        return on_failure(self.error or "")

    def recover(self, op: Callable[[str], T]) -> McbResult[T]:
        """Recover from failure with a fallback value derived from the error."""
        if self.success:
            return self
        return McbResult[T].ok(op(self.error or ""))

    def lash(self, op: Callable[[str], McbResult[T]]) -> McbResult[T]:
        """Apply recovery function on failure; return self on success."""
        if self.failure:
            return op(self.error or "")
        return self

    def filter(self, predicate: Callable[[T], bool]) -> McbResult[T]:
        """Filter success value; return failure if predicate fails."""
        if self.success and predicate(self.value):
            return self
        if self.failure:
            return self
        return self.__class__.fail(c.ERR_RESULT_FILTER_PREDICATE_FAILED)

    def flow_through(
        self,
        *funcs: Callable[[T], McbResult[T]],
    ) -> McbResult[T]:
        """Chain multiple homogeneous Result-returning operations in sequence."""
        current: McbResult[T] = self
        for func in funcs:
            if current.failure:
                return current
            current = current.flat_map(func)
        return current

    def tap(self, op: Callable[[T], None]) -> McbResult[T]:
        """Apply side effect to success value; return unchanged."""
        if self.success:
            op(self.value)
        return self

    def tap_error(self, op: Callable[[str], None]) -> McbResult[T]:
        """Apply side effect to error message; return unchanged."""
        if self.failure and self.error is not None:
            op(self.error)
        return self

    def map_error(self, op: Callable[[str], str]) -> McbResult[T]:
        """Transform error message; return unchanged on success."""
        if self.failure:
            return McbResult[T].fail(
                op(self.error or ""),
                error_code=self.error_code,
                exception=self._exception,
            )
        return self

    @overload
    def map_or(self, default: None, func: None = None) -> T | None: ...

    @overload
    def map_or[DefaultT](self, default: DefaultT, func: None = None) -> T | DefaultT: ...

    @overload
    def map_or[DefaultT](
        self,
        default: DefaultT,
        func: Callable[[T], DefaultT],
    ) -> DefaultT: ...

    def map_or[DefaultT](
        self,
        default: DefaultT,
        func: Callable[[T], DefaultT] | None = None,
    ) -> T | DefaultT:
        """Apply ``func`` to success value or return ``default``."""
        if self.success:
            if func is not None:
                return func(self.value)
            return self.value
        return default

    def unwrap(self) -> T:
        """Return the success value or raise the captured exception."""
        if self.failure:
            if self._exception is not None:
                raise self._exception
            msg = c.ERR_RESULT_CANNOT_UNWRAP.format(error=self.error)
            raise RuntimeError(msg)
        return self.value

    def unwrap_or(self, default: T) -> T:
        """Return the success value or ``default``."""
        if self.success and self._payload is not None:
            return self._payload
        return default

    def unwrap_or_else(self, op: Callable[[str], T]) -> T:
        """Return the success value or compute a fallback from the error."""
        if self.success and self._payload is not None:
            return self._payload
        return op(self.error or "")


r = McbResult


class BaseMcbSettings(BaseSettings):
    """Base settings for MCB scripts with per-class singleton lifecycle.

    Environment variables are read with the ``MCB_`` prefix, e.g.
    ``MCB_LOG_LEVEL`` maps to ``log_level``.
    """

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_prefix=c.ENV_PREFIX,
        extra="ignore",
        validate_assignment=True,
    )

    _lock: ClassVar[threading.RLock] = threading.RLock()
    _instance: ClassVar[BaseMcbSettings | None] = None
    _singleton_enabled: ClassVar[bool] = True

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        cls._instance = None

    def __new__(cls, **kwargs: Any) -> Self:
        if not cls._singleton_enabled:
            return super().__new__(cls)
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        if not isinstance(cls._instance, cls):
            msg = f"singleton instance is not of expected type {cls.__name__}"
            raise TypeError(msg)
        return cls._instance

    @classmethod
    @contextmanager
    def _singleton_disabled(cls) -> Generator[None]:
        with cls._lock:
            original = cls._singleton_enabled
            cls._singleton_enabled = False
            try:
                yield
            finally:
                cls._singleton_enabled = original

    @classmethod
    def fetch_global(cls) -> Self:
        """Return the shared per-class singleton."""
        existing = getattr(cls, "_instance", None)
        if isinstance(existing, cls):
            return existing
        return cls()

    @classmethod
    def reset_for_testing(cls) -> None:
        """Reset the per-class singleton for test isolation."""
        with cls._lock:
            cls._instance = None

    @classmethod
    def validate_overrides(cls, **overrides: Any) -> None:
        """Reject override keys that are not declared model fields."""
        unknown = sorted(set(overrides) - set(cls.model_fields))
        if unknown:
            msg = f"Unknown settings override(s) for {cls.__name__}: {', '.join(unknown)}"
            raise ValueError(msg)

    def clone(self, **overrides: Any) -> Self:
        """Deep copy with optional field overrides and re-validation."""
        self.__class__.validate_overrides(**overrides)
        with self.__class__._singleton_disabled():
            copied = self.model_copy(update=overrides, deep=True)
        copied.__pydantic_validator__.validate_python(
            copied.__dict__,
            self_instance=copied,
        )
        return copied

    @classmethod
    def update_global(cls, **overrides: Any) -> Self:
        """Replace the shared singleton via ``model_copy`` + re-validation."""
        current = cls.fetch_global()
        new_instance = current.clone(**overrides)
        with cls._lock:
            cls._instance = new_instance
        return new_instance

    @classmethod
    def resolve_env_file(cls, namespace: str | None = None) -> str:
        """Centralised ``.env`` discovery.

        Honours ``MCB_ENV_FILE``; otherwise prefers ``.env.mcb-{namespace}``
        when ``namespace`` is given and the file exists, falling back to ``.env``.
        """
        custom_env_file = os.environ.get("MCB_ENV_FILE")
        if custom_env_file:
            custom_path = Path(custom_env_file)
            if custom_path.exists():
                return str(custom_path.resolve())
            return custom_env_file
        if namespace:
            scoped = Path.cwd() / f".env.mcb-{namespace}"
            if scoped.exists():
                return str(scoped.resolve())
        default_path = Path.cwd() / ".env"
        if default_path.exists():
            return str(default_path.resolve())
        return ".env"


def configure_logging(json_format: bool = False) -> None:
    """Configure structlog for MCB scripts.

    Call once at each CLI entrypoint. In normal dev mode logs are rendered as
    plain key=value lines; set ``json_format=True`` (or ``MCB_LOG_JSON=1``) for
    JSON output suitable for CI aggregation.
    """
    use_json = json_format or os.environ.get("MCB_LOG_JSON", "").lower() in (
        "1",
        "true",
        "yes",
    )

    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.ExtraAdder(),
    ]

    formatter = structlog.processors.JSONRenderer() if use_json else structlog.dev.ConsoleRenderer()

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


class McbLogger:
    """Thin wrapper around structlog that preserves the FLEXT logger contract.

    ``fetch_logger`` returns a module-scoped bound logger. Use ``bind()`` to
    derive loggers with additional context.
    """

    _structlog_configured: ClassVar[bool] = False

    def __init__(self, name: str, *, logger: structlog.stdlib.BoundLogger) -> None:
        self.name = name
        self._logger = logger

    @classmethod
    def ensure_structlog_configured(cls) -> None:
        """Idempotently configure structlog."""
        if not cls._structlog_configured:
            configure_logging()
            cls._structlog_configured = True

    @classmethod
    def fetch_logger(cls, name: str) -> McbLogger:
        """Fetch the canonical logger for a module."""
        cls.ensure_structlog_configured()
        bound_logger = structlog.get_logger(name)
        return cls(name, logger=bound_logger)

    def bind(self, **context: Any) -> McbLogger:
        """Return a new logger with additional bound context."""
        return McbLogger(self.name, logger=self._logger.bind(**context))

    def debug(self, msg: str, **context: Any) -> McbResult[bool]:
        """Log a debug event."""
        self._logger.debug(msg, **context)
        return r[bool].ok(True)

    def info(self, msg: str, **context: Any) -> McbResult[bool]:
        """Log an info event."""
        self._logger.info(msg, **context)
        return r[bool].ok(True)

    def warning(self, msg: str, **context: Any) -> McbResult[bool]:
        """Log a warning event."""
        self._logger.warning(msg, **context)
        return r[bool].ok(True)

    def error(self, msg: str, **context: Any) -> McbResult[bool]:
        """Log an error event."""
        self._logger.error(msg, **context)
        return r[bool].ok(True)

    def exception(self, msg: str, **context: Any) -> McbResult[bool]:
        """Log an exception event."""
        self._logger.exception(msg, **context)
        return r[bool].ok(True)


def get_logger(name: str) -> McbLogger:
    """Fetch a structured logger for the given module name."""
    return McbLogger.fetch_logger(name)


class McbService(BaseModel):
    """Per-class singleton service base.

    Subclasses override :meth:`execute` to implement their behaviour and may
    access settings via :attr:`runtime_settings` if a ``BaseMcbSettings`` class
    is wired through the subclass.
    """

    model_config: ClassVar[ConfigDict] = ConfigDict(
        strict=True,
        arbitrary_types_allowed=True,
        extra="forbid",
        validate_assignment=True,
    )

    runtime_settings: BaseMcbSettings | None = None

    _lock: ClassVar[threading.RLock] = threading.RLock()
    _instance: ClassVar[Self | None] = None

    def __init_subclass__(cls, **kwargs: Unpack[ConfigDict]) -> None:
        super().__init_subclass__(**kwargs)
        cls._instance = None

    def __init__(self, **model_data: Any) -> None:
        """Validate through the canonical Pydantic validator directly."""
        self.__pydantic_validator__.validate_python(model_data, self_instance=self)

    def __new__(cls, **kwargs: Any) -> Self:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        if not isinstance(cls._instance, cls):
            msg = f"service singleton is not of expected type {cls.__name__}"
            raise TypeError(msg)
        return cls._instance

    @classmethod
    def fetch_global(cls) -> Self:
        """Return the shared per-class service singleton."""
        existing = getattr(cls, "_instance", None)
        if isinstance(existing, cls):
            return existing
        with cls._lock:
            existing = getattr(cls, "_instance", None)
            if isinstance(existing, cls):
                return existing
            instance = cls()
            cls._instance = instance
            return instance

    @classmethod
    def reset_for_testing(cls) -> None:
        """Reset the per-class service singleton for test isolation."""
        with cls._lock:
            cls._instance = None

    @classmethod
    def with_settings(cls, settings: BaseMcbSettings) -> Self:
        """Return the singleton configured with a settings clone."""
        instance = cls.fetch_global()
        instance.runtime_settings = settings.clone()
        return instance

    def execute(self) -> McbResult[Any]:
        """Run the service; subclasses override this method."""
        msg = f"{type(self).__name__}.execute() must be implemented"
        raise NotImplementedError(msg)


s = McbService


__all__ = [
    "BaseMcbSettings",
    "McbLogger",
    "McbResult",
    "McbService",
    "configure_logging",
    "get_logger",
    "r",
    "s",
]
