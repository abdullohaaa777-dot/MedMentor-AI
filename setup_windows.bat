@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo [1/4] Python 3.13 tekshirilmoqda...
py -3.13 --version
if errorlevel 1 (echo Python 3.13 o'rnatilmagan! & pause & exit /b 1)
echo [2/4] Virtual muhit...
if not exist .venv\Scripts\python.exe py -3.13 -m venv .venv
if errorlevel 1 (echo Virtual muhit xato & pause & exit /b 1)
echo [3/4] Python kutubxonalari...
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -e .
if errorlevel 1 (echo Kutubxona o'rnatilmadi. Internet aloqani tekshiring. & pause & exit /b 1)
if not exist .env copy .env.example .env >nul
echo [4/4] .env fayliga BOT_TOKEN va ANTHROPIC_API_KEY kiriting.
notepad .env
pause
