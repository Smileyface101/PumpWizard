"""Local durable storage for imported strategy packages.

This schema is intentionally separate from future wallet and position tables so
opening the initial app never creates or touches a wallet.
"""
from __future__ import annotations

from contextlib import contextmanager
import json
from pathlib import Path
import sqlite3
from typing import Iterator

from .strategies import ImportedStrategy


SCHEMA_VERSION = 1


class StrategyLibrary:
    def __init__(self, data_dir: Path):
        data_dir.mkdir(parents=True, exist_ok=True)
        self.path = data_dir / "pumpwizard.sqlite"
        self._connection = sqlite3.connect(self.path)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA journal_mode=WAL")
        self._connection.execute("PRAGMA foreign_keys=ON")
        self._initialize()

    def _initialize(self) -> None:
        with self._connection:
            self._connection.executescript("""
                CREATE TABLE IF NOT EXISTS meta (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS strategies (
                    digest TEXT PRIMARY KEY,
                    imported_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
                    schema_name TEXT NOT NULL,
                    strategy_id TEXT NOT NULL,
                    label TEXT NOT NULL,
                    strategy_version TEXT,
                    engine TEXT,
                    compatibility TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    package_json TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS strategy_library_order
                    ON strategies(strategy_id, imported_at DESC);
            """)
            current = self._connection.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()
            if current is None:
                self._connection.execute("INSERT INTO meta(key,value) VALUES('schema_version',?)", (str(SCHEMA_VERSION),))
            elif current["value"] != str(SCHEMA_VERSION):
                raise RuntimeError("Unsupported local strategy-library database version")

    def close(self) -> None:
        self._connection.close()

    def import_strategy(self, strategy: ImportedStrategy) -> bool:
        with self._connection:
            cursor = self._connection.execute("""
                INSERT OR IGNORE INTO strategies(
                    digest, schema_name, strategy_id, label, strategy_version, engine,
                    compatibility, reason, package_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (strategy.digest, strategy.schema, strategy.strategy_id, strategy.label,
                  strategy.version, strategy.engine, strategy.compatibility, strategy.reason,
                  json.dumps(strategy.package, ensure_ascii=False, sort_keys=True, separators=(",", ":"))))
        return cursor.rowcount == 1

    def rows(self) -> list[dict[str, str | None]]:
        return [dict(row) for row in self._connection.execute("""
            SELECT digest, imported_at, schema_name, strategy_id, label,
                   strategy_version, engine, compatibility, reason
            FROM strategies ORDER BY imported_at DESC, strategy_id
        """)]

    def summary(self) -> dict[str, int | str]:
        total = self._connection.execute("SELECT count(*) FROM strategies").fetchone()[0]
        compatible = self._connection.execute(
            "SELECT count(*) FROM strategies WHERE compatibility='runnable'").fetchone()[0]
        return {"database": str(self.path), "schema_version": SCHEMA_VERSION,
                "strategies": total, "runnable_strategies": compatible}


@contextmanager
def open_library(data_dir: Path) -> Iterator[StrategyLibrary]:
    library = StrategyLibrary(data_dir)
    try:
        yield library
    finally:
        library.close()

