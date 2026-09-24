"""Pure deterministic emissions calculation logic."""
from __future__ import annotations

import math
from typing import Any


BLOCKED_RESULT = {
    "status": "BLOCKED",
    "kg_co2e": None,
    "tco2e": None,
    "formula": None,
}


def _blocked(factor_unit: Any) -> dict[str, Any]:
    return {**BLOCKED_RESULT, "factor_unit": factor_unit}


def _valid_nonnegative_number(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
        and value >= 0
    )


def calculate_emissions(
    *, quantity: Any, factor_value: Any, factor_unit: Any, factor_status: Any
) -> dict[str, Any]:
    """Calculate only from a VERIFIED factor and finite non-negative numbers."""
    if factor_status != "VERIFIED":
        return _blocked(factor_unit)

    if not _valid_nonnegative_number(quantity):
        return _blocked(factor_unit)

    if not _valid_nonnegative_number(factor_value):
        return _blocked(factor_unit)

    kg = quantity * factor_value
    return {
        "status": "CALCULATED",
        "kg_co2e": kg,
        "tco2e": kg / 1000,
        "formula": f"{quantity} × {factor_value}",
        "factor_unit": factor_unit,
    }
