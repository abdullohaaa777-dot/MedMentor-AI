@echo off
chcp 65001 >nul
cd /d "%~dp0"
.venv\Scripts\python.exe -m uvicorn medmentor.web:app --host 127.0.0.1 --port 8080
pause
