@echo off
REM Build Script for MyDownloader Windows Installer
REM ==============================================

title MyDownloader Build Script
color 0A

echo.
echo ==========================================
echo  MyDownloader Build Script v3.0
echo ==========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python ist nicht installiert!
    pause
    exit /b 1
)
echo [OK] Python gefunden

REM Check pip
pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pip ist nicht installiert!
    pause
    exit /b 1
)
echo [OK] pip gefunden

REM Install/Update Requirements
echo.
echo [INFO] Installiere Dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Dependency-Installation fehlgeschlagen!
    pause
    exit /b 1
)
echo [OK] Dependencies installiert

REM Install PyInstaller if not present
echo.
echo [INFO] Pruefe PyInstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installiere PyInstaller...
    pip install pyinstaller
)
echo [OK] PyInstaller bereit

REM Clean previous builds
echo.
echo [INFO] Bereinige alte Builds...
if exist "build" rmdir /s /q "build"
if exist "dist\MyDownloader" rmdir /s /q "dist\MyDownloader"
if exist "MyDownloader.spec" del /q "MyDownloader.spec"
echo [OK] Bereinigung abgeschlossen

REM Build with PyInstaller
echo.
echo [INFO] Erstelle Executable mit PyInstaller...
echo.

pyinstaller --name=MyDownloader ^
    --onedir ^
    --windowed ^
    --icon=assets\icons\app_icon.ico ^
    --add-data "assets;assets" ^
    --hidden-import=PIL._tkinter_finder ^
    --collect-all yt_dlp ^
    --noconfirm ^
    mydownloader\__main__.py

if errorlevel 1 (
    echo.
    echo [ERROR] PyInstaller Build fehlgeschlagen!
    pause
    exit /b 1
)

echo.
echo [OK] Executable erstellt: dist\MyDownloader\MyDownloader.exe

REM Check for Inno Setup
echo.
echo [INFO] Pruefe Inno Setup...
set "INNO_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if not exist "%INNO_PATH%" (
    echo [WARNUNG] Inno Setup nicht gefunden!
    echo [INFO] Executable ist bereit unter: dist\MyDownloader\
    echo [INFO] Um einen Installer zu erstellen, installiere Inno Setup:
    echo [INFO] https://jrsoftware.org/isinfo.php
    echo.
    echo [INFO] Dann fuehre aus: "%INNO_PATH%" setup.iss
    pause
    exit /b 0
)

echo [OK] Inno Setup gefunden

REM Create Installer
echo.
echo [INFO] Erstelle Windows Installer...
"%INNO_PATH%" setup.iss

if errorlevel 1 (
    echo [ERROR] Installer-Erstellung fehlgeschlagen!
    pause
    exit /b 1
)

echo.
echo ==========================================
echo  BUILD ERFOLGREICH!
echo ==========================================
echo.
echo Executable: dist\MyDownloader\MyDownloader.exe
echo Installer:  dist\installer\MyDownloader-3.0.0-Setup.exe
echo.
echo Teste die Anwendung vor der Veroeffentlichung!
echo ==========================================
pause
