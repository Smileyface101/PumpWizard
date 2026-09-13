"""Command-line entry points shared by the packaged desktop application."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from . import __version__
from .desktop import run_desktop
from .library import open_library
from .paths import default_data_dir
from .strategies import StrategyImportError, parse_package


def _data_dir(value: str | None) -> Path:
    return Path(value).expanduser().resolve() if value else default_data_dir()


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pumpwizard", description=__doc__)
    parser.add_argument("--data-dir", help="Local application-data directory")
    parser.add_argument("--version", action="version", version=f"PumpWizard Runner {__version__}")
    commands = parser.add_subparsers(dest="command")
    commands.add_parser("desktop", help="Open the local desktop application")
    importer = commands.add_parser("import", help="Import a local strategy JSON file")
    importer.add_argument("file", type=Path)
    commands.add_parser("strategies", help="List imported strategies")
    commands.add_parser("status", help="Show local library status")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    command = args.command or "desktop"
    data_dir = _data_dir(args.data_dir)
    if command == "desktop":
        return run_desktop(data_dir)
    if command == "import":
        try:
            imported = parse_package(args.file.read_text(encoding="utf-8"))
        except OSError as exc:
            print(f"Cannot read strategy file: {exc}", file=sys.stderr)
            return 2
        except StrategyImportError as exc:
            print(f"Cannot import strategy: {exc}", file=sys.stderr)
            return 2
        with open_library(data_dir) as library:
            created = library.import_strategy(imported)
        verb = "Imported" if created else "Already in library"
        print(f"{verb}: {imported.label} ({imported.strategy_id})")
        print(f"Compatibility: {imported.compatibility}")
        print(imported.reason)
        return 0
    with open_library(data_dir) as library:
        if command == "status":
            print(json.dumps({"app_version": __version__, **library.summary()}, indent=2))
            return 0
        if command == "strategies":
            rows = library.rows()
    if not rows:
        print("No strategies imported. Use: pumpwizard import path/to/strategy.json")
        return 0
    for row in rows:
        version = row["strategy_version"] or "legacy"
        print(f"{row['strategy_id']} {version} | {row['compatibility']} | {row['label']}")
    return 0

