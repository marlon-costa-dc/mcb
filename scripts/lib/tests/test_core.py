"""Tests for scripts.lib.core — FLEXT-style primitives."""

from __future__ import annotations

import pytest

from ..core import (
    BaseMcbSettings,
    Err,
    Ok,
    Result,
    configure_logging,
    get_logger,
)


class TestResult:
    def test_ok_is_ok(self) -> None:
        result: Result[int] = Ok(42)
        assert result.is_ok
        assert not result.is_err
        assert result.unwrap() == 42

    def test_err_is_err(self) -> None:
        result: Result[int] = Err(ValueError("boom"))
        assert result.is_err
        assert not result.is_ok
        assert result.error is not None
        assert str(result.error) == "boom"

    def test_unwrap_raises(self) -> None:
        result: Result[int] = Err(ValueError("boom"))
        with pytest.raises(ValueError, match="boom"):
            result.unwrap()

    def test_unwrap_or(self) -> None:
        assert Ok(42).unwrap_or(0) == 42
        assert Err(ValueError("boom")).unwrap_or(0) == 0

    def test_unwrap_or_else(self) -> None:
        assert Ok(42).unwrap_or_else(lambda _: 0) == 42
        assert Err(ValueError("boom")).unwrap_or_else(lambda e: len(str(e))) == 4

    def test_map(self) -> None:
        assert Ok(21).map(lambda x: x * 2).unwrap() == 42
        mapped = Err(ValueError("boom")).map(lambda x: x * 2)
        assert mapped.is_err

    def test_flat_map(self) -> None:
        def double(x: int) -> Result[int]:
            return Ok(x * 2)

        assert Ok(21).flat_map(double).unwrap() == 42
        chained = Ok(21).flat_map(double).flat_map(double)
        assert chained.unwrap() == 84

        failed = Err(ValueError("boom")).flat_map(double)
        assert failed.is_err


class TestSettings:
    def test_base_settings_read_env_with_prefix(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("MCB_LOG_LEVEL", "debug")

        class Settings(BaseMcbSettings):
            log_level: str = "info"

        settings = Settings()
        assert settings.log_level == "debug"

    def test_base_settings_ignore_extra_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("MCB_UNKNOWN_VAR", "ignored")

        class Settings(BaseMcbSettings):
            log_level: str = "info"

        settings = Settings()
        assert settings.log_level == "info"


class TestLogging:
    def test_configure_logging_runs(self) -> None:
        configure_logging(json_format=False)
        logger = get_logger(__name__)
        logger.info("test.event", key="value")
