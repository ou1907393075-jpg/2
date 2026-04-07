@echo off
setlocal
cd /d %~dp0

echo [INFO] Starting game...
set RUNNER=
where py >nul 2>nul
if not errorlevel 1 set RUNNER=py -3
if "%RUNNER%"=="" (
  where python >nul 2>nul
  if not errorlevel 1 set RUNNER=python
)

if "%RUNNER%"=="" (
  echo [ERROR] Python runtime not found.
  echo Please install Python 3 from python.org and check "Add python.exe to PATH".
  echo Or build EXE on Windows: python build_windows_exe.py
  echo.
  pause
  exit /b 1
)

%RUNNER% game.py
set ERR=%ERRORLEVEL%
if not "%ERR%"=="0" (
  echo.
  echo [ERROR] Program exited with code: %ERR%
  if "%ERR%"=="9009" echo [HINT] Runtime command not found. Reinstall Python and enable PATH.
  echo Common reasons:
  echo 1^) Running inside zip. Please extract first.
  echo 2^) Python environment issue.
)

echo.
echo [INFO] Press any key to close...
pause >nul
exit /b %ERR%
