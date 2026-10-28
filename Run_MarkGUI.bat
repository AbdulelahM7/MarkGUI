@echo off
title MarkGUI Launcher
cd /d "%~dp0"

set "PY="
where py >nul 2>nul && set "PY=py"
if not defined PY where python >nul 2>nul && set "PY=python"

if not defined PY (
    echo Python is not installed. Installing Python 3.12 using winget...
    winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
    echo.
    echo Python installed. Please CLOSE this window and double-click Run_MarkGUI.bat again.
    pause
    exit /b
)

echo Checking required packages (first run may take a few minutes)...
%PY% -m pip install -q -U --disable-pip-version-check -r requirements.txt
if errorlevel 1 (
    echo.
    echo Installation failed. Check your internet connection and try again.
    pause
    exit /b
)

if "%PY%"=="py" (
    start "" pyw "%~dp0markgui.py"
) else (
    start "" pythonw "%~dp0markgui.py"
)
exit /b
