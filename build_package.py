#!/usr/bin/env python3
"""Build a downloadable package for the xianxia text game."""

from __future__ import annotations

from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parent
DIST_DIR = ROOT / "dist"
PACKAGE_DIR = DIST_DIR / "xianxia-game"
ZIP_PATH = DIST_DIR / "xianxia-game.zip"


def clean() -> None:
    if PACKAGE_DIR.exists():
        shutil.rmtree(PACKAGE_DIR)
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()


def write_launchers() -> None:
    launcher_sh = PACKAGE_DIR / "start.sh"
    launcher_sh.write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        'DIR="$(cd "$(dirname "$0")" && pwd)"\n'
        'python3 "$DIR/game.py"\n',
        encoding="utf-8",
    )
    launcher_sh.chmod(0o755)

    launcher_bat = PACKAGE_DIR / "start.bat"
    launcher_bat.write_text(
        "@echo off\r\n"
        "chcp 65001 >nul\r\n"
        "where python >nul 2>nul\r\n"
        "if errorlevel 1 (\r\n"
        "  echo [错误] 未检测到 Python，请先安装 Python 3，或使用 Windows EXE 打包版。\r\n"
        "  pause\r\n"
        "  exit /b 1\r\n"
        ")\r\n"
        "python game.py\r\n"
        "pause\r\n",
        encoding="utf-8",
    )


def build() -> None:
    DIST_DIR.mkdir(exist_ok=True)
    PACKAGE_DIR.mkdir(exist_ok=True)

    shutil.copy2(ROOT / "game.py", PACKAGE_DIR / "game.py")
    shutil.copy2(ROOT / "README.md", PACKAGE_DIR / "README.md")
    write_launchers()

    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(PACKAGE_DIR.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(DIST_DIR))


def main() -> None:
    clean()
    build()
    print(f"Package created: {ZIP_PATH}")


if __name__ == "__main__":
    main()
