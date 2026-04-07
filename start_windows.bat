@echo off
setlocal
cd /d %~dp0

echo [INFO] Starting game launcher...
where python >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Python 3 not found.
  echo Install Python 3 or use Windows EXE package.
  echo.
  pause
  exit /b 1
)

python game.py
set ERR=%ERRORLEVEL%
if not "%ERR%"=="0" (
  echo.
  echo [ERROR] Program exited with code: %ERR%
  echo Make sure the zip is extracted and Python works.
)

echo.
echo [INFO] Press any key to close...
pause >nul
exit /b %ERR%
