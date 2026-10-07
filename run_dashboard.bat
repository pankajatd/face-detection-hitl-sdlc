@echo off
title Face Detection HITL SDLC Platform Dashboard
echo =========================================================================
echo  Launching Human-In-The-Loop Multi-Agent SDLC Dashboard (Port 8509)
echo =========================================================================
"C:\Users\panka\.gemini\antigravity\scratch\ocr_multiagent_system\venv_ocr\Scripts\python.exe" -m streamlit run dashboard.py --server.port 8509
pause
