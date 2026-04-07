@echo off
setlocal
cd /d %~dp0

echo [INFO] Starting game launcher...

if exist xianxia_game.exe (
  echo [INFO] EXE detected. Running without Python...
  xianxia_game.exe
  set ERR=%ERRORLEVEL%
  echo.
  echo [INFO] Press any key to close...
  pause >nul
  exit /b %ERR%
)

set RUNNER=
where py >nul 2>nul
if not errorlevel 1 set RUNNER=py -3
if "%RUNNER%"=="" (
  where python >nul 2>nul
  if not errorlevel 1 set RUNNER=python
)

if "%RUNNER%"=="" (
  echo [ERROR] No Python runtime found.
  echo Use EXE package if you do not want Python:
  echo dist_windows\xianxia-game-windows-exe.zip
  echo.
  pause
  exit /b 1
)

%RUNNER% game.py
set ERR=%ERRORLEVEL%
if not "%ERR%"=="0" (
  echo.
  echo [ERROR] Program exited with code: %ERR%
)

echo.
echo [INFO] Press any key to close...
pause >nul
exit /b %ERR%
