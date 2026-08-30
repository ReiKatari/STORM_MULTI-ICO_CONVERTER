@echo off
title STORM MULTI-ICO LAUNCHER
echo Starting Storm Engine...
python stormmultiicoconverter.py
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Could not launch Python script.
    echo Please ensure Python is installed and libraries are present:
    echo pip install customtkinter Pillow tkinterdnd2
    echo.
    pause
)