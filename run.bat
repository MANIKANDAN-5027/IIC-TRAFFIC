@echo off
title IIC Traffic AI
echo ========================================================
echo Starting IIC Traffic AI Backend & Web Dashboard...
echo Opening http://127.0.0.1:5000 in your browser...
echo ========================================================
start "" "http://127.0.0.1:5000"
python app.py
pause
