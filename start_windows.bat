@echo off
setlocal
chcp 65001 >nul
cd /d %~dp0

echo [启动中] 修仙模拟人生（Windows 启动器）...
where python >nul 2>nul
if errorlevel 1 (
  echo [错误] 未检测到 Python 3。
  echo 请安装 Python 3，或使用 Windows EXE 打包版。
  echo.
  pause
  exit /b 1
)

python game.py
set ERR=%ERRORLEVEL%
if not "%ERR%"=="0" (
  echo.
  echo [程序异常退出] 错误码: %ERR%
  echo 请确认：已解压后再运行、Python 可用。
)

echo.
echo [结束] 按任意键关闭窗口...
pause >nul
exit /b %ERR%
