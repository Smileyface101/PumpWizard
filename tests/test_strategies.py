import json
from pathlib import Path

import pytest

from pumpwizard_runner.strategies import StrategyImportError, parse_package


ROOT = Path(__file__).parents[1]


def test_native_example_is_recognized_but_not_yet_runnable():
    strategy = parse_package((ROOT / "examples" / "xyz-local-strategy.json").read_text())
    assert strategy.schema == "pumpwizard.strategy/v2"
    assert strategy.strategy_id == "xyz-momentum-example"
    assert strategy.compatibility == "recognized-not-runnable"
    assert len(strategy.digest) == 64


def test_legacy_handoff_is_inspection_only():
    handoff = {
        "schema": "pumpwizard.strategy-handoff/v1",
        "mode": "simulation_only",
        "strategy": {"id": "xyz", "label": "XYZ"},
        "configuration": {"entry_style": "momentum"},
    }
    strategy = parse_package(handoff)
    assert strategy.compatibility == "legacy-inspection-only"
    assert "simulation" in strategy.reason.lower()


def test_missing_native_rule_is_rejected():
    package = json.loads((ROOT / "examples" / "xyz-local-strategy.json").read_text())
    del package["rules"]["max_hold_seconds"]
    with pytest.raises(StrategyImportError, match="max_hold_seconds"):
        parse_package(package)

