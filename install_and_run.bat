@echo off
setlocal
chcp 65001 >nul
cd /d %~dp0

echo [启动中] 修仙模拟人生...
where python >nul 2>nul
if errorlevel 1 (
  echo [错误] 未检测到 Python，请先安装 Python 3。
  echo 你也可以在 Windows 上运行：python build_windows_exe.py 生成无需 Python 的 EXE 版本。
  echo.
  pause
  exit /b 1
)

python game.py
set ERR=%ERRORLEVEL%
if not "%ERR%"=="0" (
  echo.
  echo [程序异常退出] 错误码: %ERR%
  echo 常见原因：
  echo 1) 直接在压缩包里运行（请先解压）
  echo 2) Python 环境异常
  echo 3) 输入流被中断
)

echo.
echo [结束] 按任意键关闭窗口...
pause >nul
exit /b %ERR%
