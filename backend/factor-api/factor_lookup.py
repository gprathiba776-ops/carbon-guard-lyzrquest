"""Deterministic emission-factor resolution for CarbonGuard.

The registry is derived from the July 2026 revised UK Government GHG
Conversion Factors flat-file representation. Numerical factor selection is
performed only with explicit deterministic constraints; embeddings and LLM
similarity are intentionally outside this authority boundary.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from config import settings

REGISTRY_PATH = Path(settings.registry_path)
YEAR = settings.year
SOURCE = settings.source


def _norm(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip().lower())


def load_registry(path: Path = REGISTRY_PATH) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, list):
        raise ValueError("Factor registry must contain a JSON array.")
    return data


REGISTRY = load_registry()


def _leaf(record: dict[str, Any]) -> str:
    path = record.get("category_path") or []
    if not path:
        return ""
    unit = _norm(record.get("unit"))
    last = _norm(path[-1])
    if last == "unknown" or last == unit:
        return str(path[-2]) if len(path) >= 2 else ""
    return str(path[-1])


def _category_components(record: dict[str, Any]) -> set[str]:
    return {
        _norm(x)
        for x in (record.get("category_path") or [])
        if x and _norm(x) != "unknown"
    }


def _activity_matches(record: dict[str, Any], activity: str) -> bool:
    query = _norm(activity)
    if not query:
        return True
    explicit = _norm(record.get("activity"))
    leaf = _norm(_leaf(record))
    return query == explicit or query == leaf or query in leaf


def _subtype_matches(record: dict[str, Any], subtype: str) -> bool:
    query = _norm(subtype)
    if not query:
        return True
    leaf = _norm(_leaf(record))
    aliases = {
        "diesel": "diesel (100% mineral diesel)",
        "mineral diesel": "diesel (100% mineral diesel)",
        "100% mineral diesel": "diesel (100% mineral diesel)",
    }
    return leaf == aliases.get(query, query)


def _base_candidates(*, scope: str, unit: str, year: int) -> list[dict[str, Any]]:
    return [
        record
        for record in REGISTRY
        if record.get("factor") is not None
        and _norm(record.get("scope")) == _norm(scope)
        and _norm(record.get("unit")) == _norm(unit)
        and record.get("year") == year
    ]


def _apply_constraints(
    candidates: list[dict[str, Any]],
    *,
    activity: str,
    category: str | None,
    fuel_subtype: str | None,
) -> list[dict[str, Any]]:
    if category:
        normalized_category = _norm(category)
        candidates = [
            record
            for record in candidates
            if normalized_category in _category_components(record)
        ]

    if activity:
        candidates = [
            record for record in candidates if _activity_matches(record, activity)
        ]

    if fuel_subtype:
        candidates = [
            record
            for record in candidates if _subtype_matches(record, fuel_subtype)
        ]

    return candidates


def _result_for_candidates(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    if len(candidates) == 1:
        match = candidates[0]
        return {
            "status": "VERIFIED",
            "reason": "Exactly one factor satisfies all supplied deterministic constraints.",
            "match": match,
            "matches": [match],
        }

    if len(candidates) > 1:
        return {
            "status": "REVIEW_REQUIRED",
            "reason": "Multiple official factors satisfy the supplied constraints; additional context is required.",
            "matches": candidates,
        }

    return {
        "status": "FACTOR_NOT_FOUND",
        "reason": "No official factor satisfies all supplied deterministic constraints.",
        "matches": [],
    }


def lookup_factor(
    *,
    scope: str,
    activity: str,
    unit: str,
    year: int,
    category: str | None = None,
    fuel_subtype: str | None = None,
) -> dict[str, Any]:
    """Return VERIFIED, REVIEW_REQUIRED, or FACTOR_NOT_FOUND deterministically."""
    if year != YEAR:
        return {
            "status": "FACTOR_NOT_FOUND",
            "reason": f"No {YEAR} factor registry is configured for year {year}.",
            "matches": [],
        }

    candidates = _base_candidates(scope=scope, unit=unit, year=year)
    candidates = _apply_constraints(
        candidates,
        activity=activity,
        category=category,
        fuel_subtype=fuel_subtype,
    )
    return _result_for_candidates(candidates)
