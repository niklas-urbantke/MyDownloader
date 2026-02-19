"""
Build Script für MyDownloader V3 Setup-Installer
Erstellt eine standalone .exe und ein Windows-Installationsprogramm
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# Konfiguration
APP_NAME = "MyDownloader"
APP_VERSION = "3.0.0"
MAIN_SCRIPT = "app_tkinter_v3.py"
ICON_FILE = "assets/icon.ico"  # Optional
OUTPUT_DIR = "dist"
BUILD_DIR = "build"

def print_step(step_num, message):
    """Gibt einen nummerierten Schritt aus"""
    print(f"\n{'='*60}")
    print(f"SCHRITT {step_num}: {message}")
    print(f"{'='*60}")

def clean_previous_builds():
    """Löscht vorherige Build-Artefakte"""
    print_step(1, "Räume vorherige Builds auf...")
    
    dirs_to_clean = [BUILD_DIR, OUTPUT_DIR, "__pycache__"]
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"  Lösche: {dir_name}")
            shutil.rmtree(dir_name, ignore_errors=True)
    
    # Lösche .spec Dateien
    for spec_file in Path(".").glob("*.spec"):
        print(f"  Lösche: {spec_file}")
        spec_file.unlink()
    
    print("  ✅ Aufräumen abgeschlossen")

def install_dependencies():
    """Installiert benötigte Dependencies"""
    print_step(2, "Installiere Dependencies...")
    
    dependencies = [
        "pyinstaller",
        "pillow",
        "yt-dlp",
    ]
    
    print("  Installiere:", ", ".join(dependencies))
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "--upgrade"] + dependencies,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("  ✅ Dependencies installiert")
    else:
        print("  ❌ Fehler beim Installieren der Dependencies:")
        print(result.stderr)
        sys.exit(1)

def create_icon():
    """Erstellt ein Standard-Icon falls keins vorhanden"""
    print_step(3, "Überprüfe Icon...")
    
    # Erstelle assets Ordner falls nicht vorhanden
    os.makedirs("assets", exist_ok=True)
    
    if not os.path.exists(ICON_FILE):
        print(f"  ⚠️ Kein Icon gefunden bei {ICON_FILE}")
        print(f"  ℹ️ Erstelle Standard-Icon...")
        
        # Verwende PIL um ein einfaches Icon zu erstellen
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Erstelle ein 256x256 Icon
            size = 256
            img = Image.new('RGB', (size, size), color='#1DB954')  # Grün
            draw = ImageDraw.Draw(img)
            
            # Zeichne ein "M" für MyDownloader
            try:
                font = ImageFont.truetype("arial.ttf", 180)
            except:
                font = ImageFont.load_default()
            
            # Zentriere Text
            text = "M"
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            position = ((size - text_width) // 2, (size - text_height) // 2 - 20)
            
            draw.text(position, text, fill='white', font=font)
            
            # Speichere als ICO
            img.save(ICON_FILE, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
            print(f"  ✅ Standard-Icon erstellt: {ICON_FILE}")
        except Exception as e:
            print(f"  ⚠️ Konnte kein Icon erstellen: {e}")
            print(f"  ℹ️ Build wird ohne Icon fortgesetzt")
    else:
        print(f"  ✅ Icon gefunden: {ICON_FILE}")

def build_exe():
    """Baut die .exe mit PyInstaller"""
    print_step(4, "Baue .exe mit PyInstaller...")
    
    # PyInstaller Kommando
    cmd = [
        "pyinstaller",
        "--name", APP_NAME,
        "--onefile",  # Alles in eine Datei
        "--windowed",  # Kein Konsolen-Fenster
        "--clean",
        "--noconfirm",
    ]
    
    # Icon hinzufügen falls vorhanden
    if os.path.exists(ICON_FILE):
        cmd.extend(["--icon", ICON_FILE])
    
    # Hidden imports für yt-dlp und tkinter
    hidden_imports = [
        "yt_dlp",
        "PIL._tkinter_finder",
        "tkinter",
        "tkinter.ttk",
        "tkinter.scrolledtext",
        "tkinter.filedialog",
        "tkinter.messagebox",
        "urllib.request",
        "urllib.parse",
        "json",
        "os",
        "re",
        "threading",
        "queue",
        "subprocess",
        "shutil",
        "zipfile",
        "glob",
        "datetime",
    ]
    
    for imp in hidden_imports:
        cmd.extend(["--hidden-import", imp])
    
    # Daten-Dateien
    # Keine zusätzlichen Daten-Dateien für tkinter_v3
    
    # Haupt-Script
    cmd.append(MAIN_SCRIPT)
    
    print(f"  Führe aus: {' '.join(cmd)}")
    print(f"  ⏳ Dies kann einige Minuten dauern...")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        exe_path = os.path.join(OUTPUT_DIR, f"{APP_NAME}.exe")
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"  ✅ .exe erfolgreich erstellt!")
            print(f"  📁 Pfad: {exe_path}")
            print(f"  📊 Größe: {size_mb:.2f} MB")
        else:
            print(f"  ❌ .exe wurde nicht gefunden bei {exe_path}")
            sys.exit(1)
    else:
        print("  ❌ PyInstaller Fehler:")
        print(result.stderr)
        sys.exit(1)

def create_installer_files():
    """Erstellt zusätzliche Dateien für den Installer"""
    print_step(5, "Erstelle Installer-Dateien...")
    
    # README für dist Ordner
    readme_content = f"""# {APP_NAME} v{APP_VERSION}

## Installation

Führen Sie `{APP_NAME}-Setup.exe` aus, um die Anwendung zu installieren.

## Standalone Version

Sie können auch `{APP_NAME}.exe` direkt ausführen ohne Installation.

## Features

- Download einzelner Videos/Songs
- Download kompletter Playlists
- Queue-System für Batch-Downloads
- Vorschau vor dem Download
- Unterstützung für MP3, M4A, FLAC, OPUS, WAV
- Untertitel-Download
- Download-History
- Dark/Light Theme
- Node.js Integration für YouTube

## Systemanforderungen

- Windows 10/11 (64-bit)
- ~100 MB freier Speicherplatz
- Internetverbindung

## Optionale Software

- Node.js (für optimale YouTube-Unterstützung)
  - Installation über Chocolatey: `choco install nodejs`

---
Made with ❤️ using Python, yt-dlp & FFmpeg
"""
    
    with open(os.path.join(OUTPUT_DIR, "README.txt"), "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("  ✅ README.txt erstellt")

def check_inno_setup():
    """Prüft ob Inno Setup installiert ist"""
    print_step(6, "Prüfe Inno Setup Installation...")
    
    # Suche nach iscc.exe
    possible_paths = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
        r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
        r"C:\Program Files\Inno Setup 5\ISCC.exe",
    ]
    
    iscc_path = None
    for path in possible_paths:
        if os.path.exists(path):
            iscc_path = path
            break
    
    if iscc_path:
        print(f"  ✅ Inno Setup gefunden: {iscc_path}")
        return iscc_path
    else:
        print("  ⚠️ Inno Setup nicht gefunden!")
        print("  ℹ️ Download von: https://jrsoftware.org/isinfo.php")
        print("  ℹ️ Installer kann manuell mit setup_v3.iss erstellt werden")
        return None

def build_installer(iscc_path):
    """Baut den Installer mit Inno Setup"""
    print_step(7, "Baue Windows Installer...")
    
    iss_file = "setup_v3.iss"
    
    if not os.path.exists(iss_file):
        print(f"  ⚠️ {iss_file} nicht gefunden!")
        print("  ℹ️ Bitte setup_v3.iss Datei erstellen")
        return False
    
    print(f"  Führe aus: {iscc_path} {iss_file}")
    result = subprocess.run([iscc_path, iss_file], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("  ✅ Installer erfolgreich erstellt!")
        
        # Suche nach dem Installer
        installer_pattern = f"{APP_NAME}-*-Setup.exe"
        installer_dir = os.path.join(OUTPUT_DIR, "installer")
        
        if os.path.exists(installer_dir):
            installers = list(Path(installer_dir).glob(installer_pattern))
            if installers:
                for installer in installers:
                    size_mb = installer.stat().st_size / (1024 * 1024)
                    print(f"  📦 Installer: {installer}")
                    print(f"  📊 Größe: {size_mb:.2f} MB")
        return True
    else:
        print("  ❌ Inno Setup Fehler:")
        print(result.stderr)
        return False

def main():
    """Hauptfunktion"""
    print("\n" + "="*60)
    print(f"  {APP_NAME} v{APP_VERSION} - Installer Build Script")
    print("="*60)
    
    try:
        # 1. Aufräumen
        clean_previous_builds()
        
        # 2. Dependencies
        install_dependencies()
        
        # 3. Icon
        create_icon()
        
        # 4. .exe bauen
        build_exe()
        
        # 5. Installer-Dateien
        create_installer_files()
        
        # 6. Inno Setup prüfen
        iscc_path = check_inno_setup()
        
        # 7. Installer bauen (wenn Inno Setup verfügbar)
        if iscc_path:
            build_installer(iscc_path)
        
        # Fertig!
        print("\n" + "="*60)
        print("  ✅ BUILD ABGESCHLOSSEN!")
        print("="*60)
        print(f"\n📁 Ausgabe-Ordner: {OUTPUT_DIR}")
        print(f"\n📦 Dateien:")
        print(f"   - {APP_NAME}.exe (Standalone)")
        if iscc_path:
            print(f"   - installer/{APP_NAME}-{APP_VERSION}-Setup.exe (Installer)")
        print("\n💡 Die .exe kann direkt ausgeführt werden (keine Installation nötig)")
        print("💡 Der Installer kann für einfache Verteilung verwendet werden")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Build abgebrochen!")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fehler: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
