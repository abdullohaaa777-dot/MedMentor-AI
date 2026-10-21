@echo off
chcp 65001 >nul
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (echo Avval setup_windows.bat ni ishga tushiring & pause & exit /b 1)
.venv\Scripts\python.exe -m medmentor.bot
pause
