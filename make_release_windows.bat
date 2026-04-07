@echo off
setlocal
cd /d %~dp0

echo [INFO] Building Windows portable release...
where python >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Python not found. Install Python 3 first.
  pause
  exit /b 1
)

python build_windows_exe.py
set ERR=%ERRORLEVEL%
if not "%ERR%"=="0" (
  echo [ERROR] Build failed with code %ERR%
  pause
  exit /b %ERR%
)

echo [OK] Done. Share this file with players:
echo dist_windows\xianxia-game-windows-exe.zip
pause
