"""Versioned, data-only strategy package parsing.

The importer deliberately preserves unsupported strategy information rather than
converting it into a similar live policy. Strategy content is data, never code.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re
from typing import Any


class StrategyImportError(ValueError):
    """A local strategy package could not be safely identified."""


_ID = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
_VERSION = re.compile(r"^[0-9]+(?:\.[0-9]+){0,2}(?:[-+][A-Za-z0-9.-]+)?$")
_REQUIRED_NATIVE_RULES = {
    "entry_style", "entry_cap_min_usd", "entry_cap_max_usd",
    "minimum_growth_fraction", "minimum_reserve_growth_usd",
    "take_profit_fraction", "stop_loss_fraction", "max_hold_seconds",
}


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def content_hash(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ImportedStrategy:
    schema: str
    strategy_id: str
    label: str
    version: str | None
    engine: str | None
    compatibility: str
    reason: str
    package: dict[str, Any]
    digest: str


def _object(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise StrategyImportError(f"{field} must be an object")
    return value


def _text(value: Any, field: str, maximum: int = 120) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise StrategyImportError(f"{field} must be non-empty text no longer than {maximum} characters")
    return value.strip()


def _finite_number(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise StrategyImportError(f"{field} must be a number")
    result = float(value)
    if result != result or result in (float("inf"), float("-inf")):
        raise StrategyImportError(f"{field} must be finite")
    return result


def parse_package(raw: str | bytes | dict[str, Any]) -> ImportedStrategy:
    """Parse native v2 packages and inspect legacy public v1 handoffs."""
    if isinstance(raw, (str, bytes)):
        try:
            value = json.loads(raw)
        except (TypeError, json.JSONDecodeError) as exc:
            raise StrategyImportError("Strategy file must contain one JSON object") from exc
    else:
        value = raw
    package = _object(value, "strategy package")
    schema = _text(package.get("schema"), "schema", 80)
    if schema == "pumpwizard.strategy/v2":
        return _parse_native(package)
    if schema == "pumpwizard.strategy-handoff/v1":
        return _parse_legacy_handoff(package)
    raise StrategyImportError(f"Unsupported strategy schema: {schema}")


def _parse_native(package: dict[str, Any]) -> ImportedStrategy:
    strategy = _object(package.get("strategy"), "strategy")
    strategy_id = _text(strategy.get("id"), "strategy.id", 64)
    if not _ID.fullmatch(strategy_id):
        raise StrategyImportError("strategy.id must contain lowercase letters, digits, and hyphens")
    label = _text(strategy.get("label"), "strategy.label")
    version = _text(strategy.get("version"), "strategy.version", 40)
    if not _VERSION.fullmatch(version):
        raise StrategyImportError("strategy.version is not a supported version string")
    engine = _text(strategy.get("engine"), "strategy.engine", 80)
    market = _object(package.get("market"), "market")
    if market.get("chain") != "solana":
        raise StrategyImportError("Only the solana market contract is supported")
    _finite_number(market.get("observation_seconds"), "market.observation_seconds")
    rules = _object(package.get("rules"), "rules")
    missing = sorted(_REQUIRED_NATIVE_RULES - set(rules))
    if missing:
        raise StrategyImportError("rules is missing: " + ", ".join(missing))
    for name in _REQUIRED_NATIVE_RULES - {"entry_style"}:
        _finite_number(rules[name], "rules." + name)
    if not isinstance(rules["entry_style"], str) or not rules["entry_style"].strip():
        raise StrategyImportError("rules.entry_style must be non-empty text")
    reason = "The package is structurally valid. Execution support begins with a later engine release."
    return ImportedStrategy(schema="pumpwizard.strategy/v2", strategy_id=strategy_id, label=label,
                            version=version, engine=engine, compatibility="recognized-not-runnable",
                            reason=reason, package=package, digest=content_hash(package))


def _parse_legacy_handoff(package: dict[str, Any]) -> ImportedStrategy:
    strategy = _object(package.get("strategy"), "strategy")
    strategy_id = _text(strategy.get("id"), "strategy.id", 64)
    if not _ID.fullmatch(strategy_id):
        raise StrategyImportError("strategy.id must contain lowercase letters, digits, and hyphens")
    label = _text(strategy.get("label"), "strategy.label")
    _object(package.get("configuration"), "configuration")
    # Public handoffs explicitly identify themselves as simulation-only and do
    # not include the complete engine/data contract needed for local execution.
    reason = ("Legacy simulation handoff stored for inspection. It lacks the complete local "
              "engine and market-data contract required for execution.")
    return ImportedStrategy(schema="pumpwizard.strategy-handoff/v1", strategy_id=strategy_id,
                            label=label, version=None, engine=None, compatibility="legacy-inspection-only",
                            reason=reason, package=package, digest=content_hash(package))

