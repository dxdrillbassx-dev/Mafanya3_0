@echo off
chcp 65001 >nul
title Mafanya 3.0 Launcher

cd /d "%~dp0"

echo Запуск Mafanya Retro Launcher...

pythonw launcher\main.py

if %errorlevel% neq 0 (
    python launcher\main.py
)

pause