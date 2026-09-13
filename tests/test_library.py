from pathlib import Path

from pumpwizard_runner.library import StrategyLibrary
from pumpwizard_runner.strategies import parse_package


ROOT = Path(__file__).parents[1]


def test_library_deduplicates_by_canonical_content(tmp_path: Path):
    strategy = parse_package((ROOT / "examples" / "xyz-local-strategy.json").read_text())
    library = StrategyLibrary(tmp_path)
    try:
        assert library.import_strategy(strategy)
        assert not library.import_strategy(strategy)
        rows = library.rows()
        assert len(rows) == 1
        assert rows[0]["strategy_id"] == "xyz-momentum-example"
    finally:
        library.close()

