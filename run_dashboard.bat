@echo off
title Face Detection HITL SDLC Platform Dashboard
echo =========================================================================
echo  Launching Human-In-The-Loop Multi-Agent SDLC Dashboard (Port 8509)
echo =========================================================================
where python >nul 2>nul
if %ERRORLEVEL% equ 0 (
    python -m streamlit run dashboard.py --server.port 8509
) else (
    "C:\Users\panka\.gemini\antigravity\scratch\ocr_multiagent_system\venv_ocr\Scripts\python.exe" -m streamlit run dashboard.py --server.port 8509
)
pause
