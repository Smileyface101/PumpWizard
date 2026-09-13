"""PyInstaller entry point.

Freezing ``__main__.py`` directly executes it as a top-level script and loses
the package context needed by relative imports. This module intentionally uses
an absolute import so source and frozen launches follow the same CLI path.
"""
from pumpwizard_runner.cli import main


raise SystemExit(main())

