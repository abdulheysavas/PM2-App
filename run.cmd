@echo off
rem PM2 App - Windows launcher
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
    py -3 "%~dp0main.py" %*
) else (
    python "%~dp0main.py" %*
)

if errorlevel 1 (
    echo.
    echo Could not start PM2 App.
    echo Make sure Python and PyQt6 are installed:
    echo   py -m pip install -r "%~dp0requirements.txt"
    pause
)
endlocal
