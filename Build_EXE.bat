@echo off
title Build MarkGUI.exe
cd /d "%~dp0"

set "PY="
where py >nul 2>nul && set "PY=py"
if not defined PY where python >nul 2>nul && set "PY=python"
if not defined PY (
    echo Python is not installed. Run Run_MarkGUI.bat first, it installs Python for you.
    pause
    exit /b
)

echo [1/3] Installing build tools and packages (a few minutes the first time)...
%PY% -m pip install -q -U --disable-pip-version-check pyinstaller -r requirements.txt
if errorlevel 1 goto :fail

echo [2/3] Building the program (this can take 5-10 minutes)...
%PY% -m PyInstaller --noconfirm --clean --windowed --name MarkGUI ^
  --collect-all markitdown --collect-all magika --collect-all tkinterdnd2 ^
  --collect-all onnxruntime --copy-metadata markitdown --copy-metadata magika ^
  markgui.py
if errorlevel 1 goto :fail

copy /y LICENSE "dist\MarkGUI\LICENSE" >nul
copy /y THIRD_PARTY_NOTICES.md "dist\MarkGUI\THIRD_PARTY_NOTICES.md" >nul

echo [3/3] Done.
echo.
echo Your program is here:  %~dp0dist\MarkGUI\MarkGUI.exe
echo Keep the whole "MarkGUI" folder together (zip it to share it).
explorer "%~dp0dist\MarkGUI"
pause
exit /b

:fail
echo.
echo Build failed. Copy the last lines above and send them to the project maintainer.
pause
exit /b 1
