"""Tests for scripts.lib.core — FLEXT-style kernel.

Copyright (c) 2025 MCB Contributors. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest
from pydantic import BaseModel

from ..core import (
    BaseMcbSettings,
    McbLogger,
    McbResult,
    McbService,
    configure_logging,
    get_logger,
    r,
    s,
)


class TestResult:
    def test_ok_is_ok(self) -> None:
        result: McbResult[int] = r[int].ok(42)
        assert result.is_ok
        assert not result.is_err
        assert result.unwrap() == 42
        assert result.value == 42
        assert bool(result)
        assert repr(result) == "r[T].ok(42)"

    def test_err_is_err(self) -> None:
        result: McbResult[int] = r[int].fail("boom", error_code="E001")
        assert result.is_err
        assert not result.is_ok
        assert not bool(result)
        assert result.error == "boom"
        assert result.error_code == "E001"
        assert repr(result) == "r[T].fail('boom')"

    def test_unwrap_raises_captured_exception(self) -> None:
        exc = ValueError("boom")
        result: McbResult[int] = r[int].fail("boom", exception=exc)
        with pytest.raises(ValueError, match="boom"):
            result.unwrap()

    def test_unwrap_raises_on_failure_without_exception(self) -> None:
        result: McbResult[int] = r[int].fail("boom")
        with pytest.raises(RuntimeError, match="boom"):
            result.unwrap()

    def test_or_operator(self) -> None:
        assert (r[int].ok(42) | 0) == 42
        assert (r[int].fail("boom") | 0) == 0

    def test_context_manager(self) -> None:
        with r[int].ok(42) as value:
            assert value.unwrap() == 42

    def test_unwrap_or(self) -> None:
        assert r[int].ok(42).unwrap_or(0) == 42
        assert r[int].fail("boom").unwrap_or(0) == 0

    def test_unwrap_or_else(self) -> None:
        assert r[int].ok(42).unwrap_or_else(lambda _: 0) == 42
        assert r[int].fail("boom").unwrap_or_else(lambda e: len(e)) == 4

    def test_map(self) -> None:
        assert r[int].ok(21).map(lambda x: x * 2).unwrap() == 42
        mapped = r[int].fail("boom").map(lambda x: x * 2)
        assert mapped.is_err

    def test_flat_map(self) -> None:
        def double(x: int) -> McbResult[int]:
            return r[int].ok(x * 2)

        assert r[int].ok(21).flat_map(double).unwrap() == 42
        chained = r[int].ok(21).flat_map(double).flat_map(double)
        assert chained.unwrap() == 84

        failed = r[int].fail("boom").flat_map(double)
        assert failed.is_err

    def test_map_catches_exceptions(self) -> None:
        result = r[int].ok(21).map(lambda _: 1 / 0)
        assert result.is_err
        assert "division" in result.error.lower()
        assert result.exception is not None

    def test_fold(self) -> None:
        ok_result = r[int].ok(21)
        assert ok_result.fold(lambda _: -1, lambda v: v * 2) == 42

        err_result = r[int].fail("boom")
        assert err_result.fold(lambda e: len(e), lambda _: 0) == 4

    def test_recover(self) -> None:
        assert r[int].ok(42).recover(lambda _: 0).unwrap() == 42
        assert r[int].fail("boom").recover(lambda _: 7).unwrap() == 7

    def test_lash(self) -> None:
        assert r[int].ok(42).lash(lambda _: r[int].ok(99)).unwrap() == 42
        recovered = r[int].fail("boom").lash(lambda _: r[int].ok(7))
        assert recovered.unwrap() == 7

    def test_filter(self) -> None:
        assert r[int].ok(42).filter(lambda x: x > 10).unwrap() == 42
        filtered = r[int].ok(5).filter(lambda x: x > 10)
        assert filtered.is_err
        assert r[int].fail("boom").filter(lambda x: x > 10).is_err

    def test_flow_through(self) -> None:
        def add_one(x: int) -> McbResult[int]:
            return r[int].ok(x + 1)

        result = r[int].ok(1).flow_through(add_one, add_one, add_one)
        assert result.unwrap() == 4

        def fail(_x: int) -> McbResult[int]:
            return r[int].fail("stop")

        halted = r[int].ok(1).flow_through(add_one, fail, add_one)
        assert halted.is_err

    def test_tap(self) -> None:
        side_effect: list[int] = []
        result = r[int].ok(42).tap(side_effect.append)
        assert result.is_ok
        assert side_effect == [42]

        r[int].fail("boom").tap(side_effect.append)
        assert side_effect == [42]

    def test_tap_error(self) -> None:
        side_effect: list[str] = []
        result = r[int].fail("boom").tap_error(side_effect.append)
        assert result.is_err
        assert side_effect == ["boom"]

        r[int].ok(42).tap_error(side_effect.append)
        assert side_effect == ["boom"]

    def test_map_error(self) -> None:
        result = r[int].fail("boom").map_error(lambda e: e.upper())
        assert result.error == "BOOM"

        unchanged = r[int].ok(42).map_error(lambda e: e.upper())
        assert unchanged.is_ok

    def test_map_or(self) -> None:
        assert r[int].ok(42).map_or(0) == 42
        assert r[int].fail("boom").map_or(0) == 0
        assert r[int].ok(21).map_or(0, lambda x: x * 2) == 42
        assert r[int].fail("boom").map_or(0, lambda x: x * 2) == 0

    def test_fail_op(self) -> None:
        result = r[int].fail_op("load")
        assert result.is_err
        assert "load failed" in result.error

        with_exception = r[int].fail_op("load", ValueError("missing"))
        assert with_exception.is_err
        assert "load failed: missing" in with_exception.error
        assert isinstance(with_exception.exception, ValueError)

    def test_from_validation(self) -> None:
        class User(BaseModel):
            name: str
            age: int

        result = McbResult.from_validation({"name": "Ada", "age": 36}, User)
        assert result.is_ok
        assert result.value.name == "Ada"

        invalid = McbResult.from_validation({"name": "Ada"}, User)
        assert invalid.is_err

    def test_accumulate_errors(self) -> None:
        results = [
            r[int].ok(1),
            r[int].ok(2),
            r[int].ok(3),
        ]
        combined = McbResult.accumulate_errors(*results)
        assert combined.is_ok
        assert list(combined.value) == [1, 2, 3]

        mixed = [
            r[int].ok(1),
            r[int].fail("a"),
            r[int].fail("b"),
        ]
        combined = McbResult.accumulate_errors(*mixed)
        assert combined.is_err
        assert "a" in combined.error
        assert "b" in combined.error

    def test_safe_decorator(self) -> None:
        @McbResult.safe
        def double(x: int) -> int:
            return x * 2

        assert double(21).unwrap() == 42

        @McbResult.safe
        def explode() -> int:
            raise ValueError("boom")

        result = explode()
        assert result.is_err
        assert "boom" in result.error


class TestSettings:
    def test_base_settings_read_env_with_prefix(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("MCB_LOG_LEVEL", "debug")
        BaseMcbSettings.reset_for_testing()

        class Settings(BaseMcbSettings):
            log_level: str = "info"

        settings = Settings.fetch_global()
        assert settings.log_level == "debug"
        BaseMcbSettings.reset_for_testing()

    def test_base_settings_ignore_extra_env(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("MCB_UNKNOWN_VAR", "ignored")
        BaseMcbSettings.reset_for_testing()

        class Settings(BaseMcbSettings):
            log_level: str = "info"

        settings = Settings.fetch_global()
        assert settings.log_level == "info"
        BaseMcbSettings.reset_for_testing()

    def test_singleton_fetch_global(self) -> None:
        BaseMcbSettings.reset_for_testing()

        class Settings(BaseMcbSettings):
            name: str = "default"

        first = Settings.fetch_global()
        second = Settings.fetch_global()
        assert first is second
        BaseMcbSettings.reset_for_testing()

    def test_clone_is_isolated(self) -> None:
        BaseMcbSettings.reset_for_testing()

        class Settings(BaseMcbSettings):
            name: str = "default"

        global_settings = Settings.fetch_global()
        clone = global_settings.clone(name="cloned")
        assert clone.name == "cloned"
        assert global_settings.name == "default"
        BaseMcbSettings.reset_for_testing()

    def test_update_global_propagates(self) -> None:
        BaseMcbSettings.reset_for_testing()

        class Settings(BaseMcbSettings):
            name: str = "default"

        Settings.update_global(name="updated")
        assert Settings.fetch_global().name == "updated"
        BaseMcbSettings.reset_for_testing()

    def test_validate_overrides_rejects_unknown(self) -> None:
        BaseMcbSettings.reset_for_testing()

        class Settings(BaseMcbSettings):
            name: str = "default"

        with pytest.raises(ValueError, match="Unknown settings override"):
            Settings.validate_overrides(unknown="value")
        BaseMcbSettings.reset_for_testing()


class TestLogging:
    def test_configure_logging_runs(self) -> None:
        configure_logging(json_format=False)
        logger = get_logger(__name__)
        log_result = logger.info("test.event", key="value")
        assert log_result.is_ok

    def test_logger_bind(self) -> None:
        configure_logging(json_format=False)
        logger = get_logger(__name__).bind(request_id="abc")
        assert isinstance(logger, McbLogger)
        assert logger.info("bound.event").is_ok


class TestService:
    def test_service_singleton(self) -> None:
        class DemoService(McbService):
            pass

        DemoService.reset_for_testing()
        first = DemoService.fetch_global()
        second = DemoService.fetch_global()
        assert first is second
        DemoService.reset_for_testing()

    def test_service_execute_not_implemented(self) -> None:
        class DemoService(McbService):
            pass

        DemoService.reset_for_testing()
        service = DemoService.fetch_global()
        with pytest.raises(NotImplementedError):
            service.execute()
        DemoService.reset_for_testing()

    def test_service_alias(self) -> None:
        class SettingsService(s):
            pass

        SettingsService.reset_for_testing()
        assert isinstance(SettingsService.fetch_global(), McbService)
        SettingsService.reset_for_testing()

    def test_service_with_settings(self) -> None:
        BaseMcbSettings.reset_for_testing()

        class Settings(BaseMcbSettings):
            name: str = "default"

        class DemoService(McbService):
            pass

        DemoService.reset_for_testing()
        service = DemoService.with_settings(Settings.fetch_global())
        assert service.runtime_settings.name == "default"
        DemoService.reset_for_testing()
        BaseMcbSettings.reset_for_testing()
