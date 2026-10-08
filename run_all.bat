@echo off
title Face Detection HITL SDLC Platform Verification
echo =========================================================================
echo  Executing Full Automated Verification Suite (Pytest)
echo =========================================================================
where python >nul 2>nul
if %ERRORLEVEL% equ 0 (
    python -m pytest -v
) else (
    "C:\Users\panka\.gemini\antigravity\scratch\ocr_multiagent_system\venv_ocr\Scripts\python.exe" -m pytest -v
)
echo =========================================================================
pause
