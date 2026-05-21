@echo off
echo Building SysForge IT Command Center...
echo.

:: Clean previous build
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

:: Install requirements
pip install -r requirements.txt

:: Build executable
pyinstaller --onefile ^
    --windowed ^
    --name "SysForge" ^
    --icon="assets/icon.ico" ^
    --add-data "assets;assets" ^
    --hidden-import customtkinter ^
    --hidden-import psutil ^
    --hidden-import threading ^
    --hidden-import queue ^
    --hidden-import subprocess ^
    --hidden-import ctypes ^
    --hidden-import winreg ^
    --uac-admin ^
    main.py

echo.
echo Build complete! Check the 'dist' folder for SysForge.exe
pause