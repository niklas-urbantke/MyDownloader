@echo off
title Music Playlist Downloader
cd /d "%~dp0"

echo ========================================
echo  Music Playlist Downloader
echo ========================================
echo.
echo Starte App...
echo.

REM Aktiviere Virtual Environment
call .venv\Scripts\activate.bat

REM Starte Tkinter-App
python app_tkinter.py

REM Falls Fehler auftreten, Fenster nicht sofort schließen
if errorlevel 1 (
    echo.
    echo ========================================
    echo  FEHLER beim Starten der App!
    echo ========================================
    echo.
    pause
)
