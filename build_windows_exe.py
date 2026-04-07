#!/usr/bin/env python3
"""Build a Windows standalone executable package using PyInstaller.

Usage (on Windows):
  pip install pyinstaller
  python build_windows_exe.py
"""

from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parent
BUILD_DIR = ROOT / "dist_windows"
PYI_DIST = ROOT / "dist"
PYI_BUILD = ROOT / "build"
EXE_NAME = "xianxia_game.exe"
EXE_PATH = PYI_DIST / EXE_NAME
ZIP_PATH = BUILD_DIR / "xianxia-game-windows-exe.zip"


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def clean() -> None:
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    if PYI_BUILD.exists():
        shutil.rmtree(PYI_BUILD)
    if EXE_PATH.exists():
        EXE_PATH.unlink()


def build_exe() -> None:
    run([
        "pyinstaller",
        "--onefile",
        "--name",
        "xianxia_game",
        str(ROOT / "game.py"),
    ])


def package() -> None:
    BUILD_DIR.mkdir(exist_ok=True)
    shutil.copy2(EXE_PATH, BUILD_DIR / EXE_NAME)
    shutil.copy2(ROOT / "README.md", BUILD_DIR / "README.md")

    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(BUILD_DIR.iterdir()):
            if path.is_file() and path.name != ZIP_PATH.name:
                zf.write(path, path.name)


def main() -> None:
    clean()
    build_exe()
    package()
    print(f"Windows EXE package created: {ZIP_PATH}")


if __name__ == "__main__":
    main()
