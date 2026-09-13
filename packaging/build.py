"""Create a native-folder application bundle and a distributable archive."""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import platform
import shutil
import subprocess
import sys


ROOT = Path(__file__).parents[1]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "release-artifacts")
    args = parser.parse_args()
    dist = ROOT / "dist"
    build = ROOT / "build"
    for directory in (dist, build):
        if directory.exists():
            shutil.rmtree(directory)
    subprocess.run([sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "--onedir",
                    "--windowed", "--name", "PumpWizard", str(ROOT / "src" / "pumpwizard_runner" / "launcher.py")],
                   check=True, cwd=ROOT)
    args.output.mkdir(parents=True, exist_ok=True)
    system = platform.system().lower().replace("darwin", "macos")
    archive_base = args.output / f"PumpWizard-{system}-{platform.machine().lower()}"
    archive = Path(shutil.make_archive(str(archive_base), "zip", dist))
    checksums = args.output / "SHA256SUMS.txt"
    checksums.write_text(f"{sha256(archive)}  {archive.name}\n", encoding="utf-8")
    print(archive)


if __name__ == "__main__":
    main()
