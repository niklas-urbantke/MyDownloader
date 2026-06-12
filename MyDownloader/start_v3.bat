@echo off
title Ultimate Music & Video Downloader v3.0
color 0A

echo.
echo ========================================
echo  Ultimate Music ^& Video Downloader v3.0
echo ========================================
echo.

REM Prüfe ob Python installiert ist
python --version >nul 2>&1
if errorlevel 1 (
    echo [FEHLER] Python ist nicht installiert!
    echo Bitte Python von https://www.python.org/ installieren
    pause
    exit /b 1
)

echo [OK] Python gefunden
echo.

REM Prüfe ob requirements installiert sind
echo Pruefe Abhaengigkeiten...
pip show yt-dlp >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installiere benoetigte Pakete...
    echo.
    pip install -r requirements.txt
    echo.
    if errorlevel 1 (
        echo [FEHLER] Installation fehlgeschlagen!
        pause
        exit /b 1
    )
    echo [OK] Pakete installiert
) else (
    echo [OK] Abhaengigkeiten vorhanden
)

echo.
echo ========================================
echo  Starte Anwendung...
echo ========================================
echo.

REM Starte die Anwendung
python app_tkinter_v3.py

if errorlevel 1 (
    echo.
    echo [FEHLER] Anwendung konnte nicht gestartet werden!
    pause
)
