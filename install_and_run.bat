@echo off
setlocal
cd /d %~dp0

echo [INFO] Starting game...
where python >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Python 3 not found.
  echo Install Python 3, or run: python build_windows_exe.py
  echo.
  pause
  exit /b 1
)

python game.py
set ERR=%ERRORLEVEL%
if not "%ERR%"=="0" (
  echo.
  echo [ERROR] Program exited with code: %ERR%
  echo Common reasons:
  echo 1^) Running directly inside zip. Please extract first.
  echo 2^) Python environment issue.
)

echo.
echo [INFO] Press any key to close...
pause >nul
exit /b %ERR%
