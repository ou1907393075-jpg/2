@echo off
setlocal
cd /d %~dp0

echo [INFO] Starting game launcher...
set RUNNER=
where py >nul 2>nul
if not errorlevel 1 set RUNNER=py -3
if "%RUNNER%"=="" (
  where python >nul 2>nul
  if not errorlevel 1 set RUNNER=python
)

if "%RUNNER%"=="" (
  echo [ERROR] Python runtime not found.
  echo Install Python 3 and enable PATH, or use EXE package.
  echo.
  pause
  exit /b 1
)

%RUNNER% game.py
set ERR=%ERRORLEVEL%
if not "%ERR%"=="0" (
  echo.
  echo [ERROR] Program exited with code: %ERR%
  if "%ERR%"=="9009" echo [HINT] Runtime command not found. Install Python 3 with PATH enabled.
  echo Make sure zip is extracted and runtime works.
)

echo.
echo [INFO] Press any key to close...
pause >nul
exit /b %ERR%
