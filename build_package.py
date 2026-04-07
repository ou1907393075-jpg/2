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
        "setlocal\r\n"
        "echo [INFO] Starting game launcher...\r\n"
        "set ERR=0\r\n"
        "if exist xianxia_game.exe (\r\n"
        "  echo [INFO] EXE detected. Running without Python...\r\n"
        "  xianxia_game.exe\r\n"
        "  set ERR=%ERRORLEVEL%\r\n"
        "  goto :end\r\n"
        ")\r\n"
        "where py >nul 2>nul\r\n"
        "if not errorlevel 1 (\r\n"
        "  echo [INFO] Using: py -3 -u game.py\r\n"
        "  py -3 -u game.py\r\n"
        "  set ERR=%ERRORLEVEL%\r\n"
        "  goto :after_run\r\n"
        ")\r\n"
        "where python >nul 2>nul\r\n"
        "if not errorlevel 1 (\r\n"
        "  echo [INFO] Using: python -u game.py\r\n"
        "  python -u game.py\r\n"
        "  set ERR=%ERRORLEVEL%\r\n"
        "  goto :after_run\r\n"
        ")\r\n"
        "  echo [ERROR] No Python runtime found.\r\n"
        "  echo Use EXE package if you do not want Python: dist_windows\\xianxia-game-windows-exe.zip\r\n"
        "  set ERR=9009\r\n"
        "  goto :end\r\n"
        ":after_run\r\n"
        "if not \"%ERR%\"==\"0\" (\r\n"
        "  echo.\r\n"
        "  echo [ERROR] Program exited with code: %ERR%\r\n"
        "  if \"%ERR%\"==\"9009\" echo [HINT] Command not found. Check py/python installation.\r\n"
        ")\r\n"
        ":end\r\n"
        "echo.\r\n"
        "echo [INFO] Press any key to close...\r\n"
        "pause >nul\r\n"
        "exit /b %ERR%\r\n",
        encoding="utf-8",
    )


def build() -> None:
    DIST_DIR.mkdir(exist_ok=True)
    PACKAGE_DIR.mkdir(exist_ok=True)

    shutil.copy2(ROOT / "game.py", PACKAGE_DIR / "game.py")
    shutil.copy2(ROOT / "README.md", PACKAGE_DIR / "README.md")
    if (ROOT / "install_and_run.sh").exists():
        shutil.copy2(ROOT / "install_and_run.sh", PACKAGE_DIR / "install_and_run.sh")
        (PACKAGE_DIR / "install_and_run.sh").chmod(0o755)
    if (ROOT / "install_and_run.bat").exists():
        shutil.copy2(ROOT / "install_and_run.bat", PACKAGE_DIR / "install_and_run.bat")
    if (ROOT / "start_windows.bat").exists():
        shutil.copy2(ROOT / "start_windows.bat", PACKAGE_DIR / "start_windows.bat")
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
