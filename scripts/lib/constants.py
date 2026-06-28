"""MCB Python tooling constants.

Copyright (c) 2025 MCB Contributors. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Final


class McbConstants:
    """Project-wide constants for MCB Python automation."""

    # -- Environment / encoding --
    ENV_PREFIX: Final[str] = "MCB_"
    DEFAULT_ENCODING: Final[str] = "utf-8"

    # -- Result error templates --
    ERR_RESULT_CANNOT_ACCESS_VALUE: Final[str] = "Cannot access value of failed result: {error}"
    ERR_RESULT_CANNOT_UNWRAP: Final[str] = "Cannot unwrap failed result: {error}"
    ERR_RESULT_FILTER_PREDICATE_FAILED: Final[str] = "Value did not pass filter predicate"

    # -- Common exception tuples for boundary catches --
    EXC_BROAD_RUNTIME: Final[tuple[type[Exception], ...]] = (
        ArithmeticError,
        AttributeError,
        KeyError,
        LookupError,
        OSError,
        RuntimeError,
        TypeError,
        ValueError,
    )
    """Broad runtime catch for adapter-internal flows (no IO, no import)."""

    EXC_VALIDATION_TYPE_VALUE: Final[tuple[type[Exception], ...]] = (
        TypeError,
        ValueError,
    )
    """Minimal type-validation catch for value-coercion boundaries."""


c = McbConstants

__all__ = ["McbConstants", "c"]
