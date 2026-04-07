@echo off
chcp 65001 >nul
where python >nul 2>nul
if errorlevel 1 (
  echo [错误] 未检测到 Python，请先安装 Python 3。
  echo 你也可以在 Windows 上运行：python build_windows_exe.py 生成无需 Python 的 EXE 版本。
  pause
  exit /b 1
)
cd /d %~dp0
python game.py
pause
