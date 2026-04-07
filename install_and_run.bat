@echo off
setlocal
cd /d %~dp0

echo [INFO] Starting game...
echo [INFO] If game starts correctly, you will see prompt: 请输入道号
set ERR=0

if exist xianxia_game.exe (
  echo [INFO] EXE detected. Running without Python...
  xianxia_game.exe
  set ERR=%ERRORLEVEL%
  goto :end
)

where py >nul 2>nul
if not errorlevel 1 (
  echo [INFO] Using: py -3 -u game.py
  py -3 -u game.py
  set ERR=%ERRORLEVEL%
  goto :after_run
)

where python >nul 2>nul
if not errorlevel 1 (
  echo [INFO] Using: python -u game.py
  python -u game.py
  set ERR=%ERRORLEVEL%
  goto :after_run
)

echo [ERROR] No Python runtime found.
echo Use EXE package: dist_windows\xianxia-game-windows-exe.zip
set ERR=9009
goto :end

:after_run
if not "%ERR%"=="0" (
  echo.
  echo [ERROR] Program exited with code: %ERR%
  if "%ERR%"=="9009" echo [HINT] Command not found. Check py/python installation.
)

:end
echo.
echo [INFO] Press any key to close...
pause >nul
exit /b %ERR%
