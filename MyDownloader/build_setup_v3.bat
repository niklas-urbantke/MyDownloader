@echo off
REM Build Script für MyDownloader V3 Setup
REM Erstellt standalone .exe und Installer

echo ================================================
echo   MyDownloader V3 - Setup Builder
echo ================================================
echo.

REM Prüfe ob Python verfügbar ist
python --version >nul 2>&1
if errorlevel 1 (
    echo FEHLER: Python nicht gefunden!
    echo Bitte installieren Sie Python 3.8 oder neuer.
    pause
    exit /b 1
)

echo Starte Build-Prozess...
echo.

REM Aktiviere Virtual Environment falls vorhanden
if exist "..\..venv\Scripts\activate.bat" (
    echo Aktiviere Virtual Environment...
    call ..\..venv\Scripts\activate.bat
)

REM Führe Build-Script aus
python build_installer_v3.py

if errorlevel 1 (
    echo.
    echo ================================================
    echo   BUILD FEHLGESCHLAGEN!
    echo ================================================
    pause
    exit /b 1
)

echo.
echo ================================================
echo   BUILD ERFOLGREICH!
echo ================================================
echo.
echo Die Dateien befinden sich im 'dist' Ordner:
echo   - MyDownloader.exe (Standalone)
echo   - installer\MyDownloader-3.0.0-Setup.exe (Installer)
echo.
echo Drücken Sie eine Taste zum Beenden...
pause >nul
