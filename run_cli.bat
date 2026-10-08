@echo off
title Face Detection HITL SDLC Platform CLI
echo =========================================================================
echo  Launching Interactive Human-In-The-Loop CLI Session
echo =========================================================================
where python >nul 2>nul
if %ERRORLEVEL% equ 0 (
    python run_interactive_sdlc.py
) else (
    "C:\Users\panka\.gemini\antigravity\scratch\ocr_multiagent_system\venv_ocr\Scripts\python.exe" run_interactive_sdlc.py
)
pause
