@echo off
echo Starting YouTube Downloader GUI...
"C:\pinokio\bin\miniconda\python.exe" "%~dp0downloader_gui.py"
if %errorlevel% neq 0 (
    echo.
    echo Application exited with an error.
    pause
)
