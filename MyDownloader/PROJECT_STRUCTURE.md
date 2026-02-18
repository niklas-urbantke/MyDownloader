# 📦 MyDownloader - Professionelle Projektstruktur v3.0

## 🏗️ Projektarchitektur

```
MyDownloader/
├── 📄 setup.py                     # Python Package Setup
├── 📄 setup.iss                    # Windows Installer Setup (Inno Setup)
├── 📄 build.bat                    # Windows Build Script
├── 📄 requirements.txt             # Python Dependencies
├── 📄 .gitignore                   # Git Ignore Rules
├── 📄 README_V3.md                 # Benutzer-Dokumentation
├── 📄 SCHNELLSTART_V3.md          # Quick Start Guide
├── 📄 FEATURE_VERGLEICH.md        # Feature-Vergleich
├── 📄 PROJECT_STRUCTURE.md        # Diese Datei
│
├── 📁 mydownloader/               # Haupt-Package
│   ├── __init__.py                # Package Init
│   ├── __main__.py                # Entry Point
│   ├── config.py                  # Konfigurations-Manager
│   ├── constants.py               # Konstanten
│   │
│   ├── 📁 core/                   # Kern-Logik
│   │   ├── __init__.py
│   │   ├── ffmpeg.py             # FFmpeg Manager
│   │   ├── youtube.py            # YouTube API Wrapper
│   │   ├── downloader.py         # Download-Engine
│   │   └── queue_manager.py      # Queue Management
│   │
│   ├── 📁 gui/                    # Benutzeroberfläche
│   │   ├── __init__.py
│   │   ├── main_window.py        # Hauptfenster
│   │   ├── 📁 tabs/              # Tab-Module (geplant)
│   │   ├── 📁 widgets/           # Custom Widgets (geplant)
│   │   └── themes.py             # Theme-Verwaltung (geplant)
│   │
│   ├── 📁 utils/                  # Hilfsfunktionen
│   │   ├── __init__.py
│   │   ├── logger.py             # Logging-System
│   │   ├── file_utils.py         # Datei-Operationen
│   │   └── validators.py         # Eingabe-Validierung
│   │
│   └── 📁 data/                   # Daten-Verwaltung
│       ├── __init__.py
│       ├── settings.py           # Einstellungs-Manager
│       └── history.py            # Verlaufs-Manager
│
├── 📁 assets/                     # Ressourcen
│   ├── 📁 icons/
│   │   └── app_icon.ico          # App-Icon
│   └── 📁 images/                 # Bilder
│
├── 📁 tests/                      # Unit Tests (optional)
│   ├── __init__.py
│   └── test_*.py
│
├── 📁 dist/                       # Build-Output
│   ├── 📁 MyDownloader/          # PyInstaller Output
│   └── 📁 installer/              # Installer Output
│
└── 📁 build/                      # Temporäre Build-Dateien
```

## 🎯 Modul-Übersicht

### Core-Module (`mydownloader/core/`)

#### 1. **ffmpeg.py** - FFmpeg Manager
- ✅ Prüft FFmpeg-Installation
- ✅ Lädt portable Version herunter
- ✅ Verwaltet PATH-Einträge
- ✅ System-Installation-Detection

**Kern-Klasse:** `FFmpegManager`

**Verwendung:**
```python
from mydownloader.core.ffmpeg import ffmpeg_manager

if ffmpeg_manager.check_availability():
    print("FFmpeg ist verfügbar!")
```

#### 2. **youtube.py** - YouTube Downloader
- ✅ Video-Info abrufen
- ✅ Playlist-Info abrufen
- ✅ Titel-Parsing (Artist - Song)
- ✅ yt-dlp Update-Funktion

**Kern-Klasse:** `YouTubeDownloader`

**Verwendung:**
```python
from mydownloader.core.youtube import youtube_downloader

info = youtube_downloader.get_video_info(url)
playlist = youtube_downloader.get_playlist_info(playlist_url)
```

#### 3. **downloader.py** - Download Engine
- ✅ Download-Logik
- ✅ Format-Konvertierung
- ✅ Progress-Tracking
- ✅ Error-Handling

**Kern-Klasse:** `Downloader`

**Verwendung:**
```python
from mydownloader.core.downloader import downloader

success = downloader.download(
    url=video_url,
    output_dir="/path/to/output",
    settings=settings_dict,
    progress_callback=my_callback
)
```

#### 4. **queue_manager.py** - Queue Management
- ✅ Warteschlangen-Verwaltung
- ✅ Batch-Processing
- ✅ Thread-sicher
- ✅ Progress-Callbacks

**Kern-Klasse:** `QueueManager`

**Verwendung:**
```python
from mydownloader.core.queue_manager import queue_manager

queue_manager.add(url)
queue_manager.start_processing(output_dir, settings)
```

### Utils-Module (`mydownloader/utils/`)

#### 1. **logger.py** - Logging System
- ✅ Zentrales Logging
- ✅ File + Console Output
- ✅ Rotating File Handler
- ✅ Konfigurierbare Level

**Funktionen:**
```python
from mydownloader.utils.logger import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)
logger.info("Test message")
```

#### 2. **file_utils.py** - Datei-Operationen
- ✅ Dateinamen bereinigen
- ✅ Verzeichnisse erstellen
- ✅ Pfad-Sicherheit
- ✅ Größen-Formatierung

**Funktionen:**
```python
from mydownloader.utils.file_utils import clean_filename, ensure_directory

safe_name = clean_filename("Artist - Song.mp3")
ensure_directory("/path/to/dir")
```

#### 3. **validators.py** - Eingabe-Validierung
- ✅ URL-Validierung
- ✅ YouTube-URL-Erkennung
- ✅ Format-Validierung
- ✅ Einstellungs-Validierung

**Funktionen:**
```python
from mydownloader.utils.validators import is_youtube_url, validate_audio_format

if is_youtube_url(url):
    # Process URL
    pass
```

### Data-Module (`mydownloader/data/`)

#### 1. **settings.py** - Einstellungs-Manager
- ✅ Einstellungen laden/speichern
- ✅ JSON-Persistenz
- ✅ Import/Export
- ✅ Property-Access

**Kern-Klasse:** `SettingsManager`

**Verwendung:**
```python
from mydownloader.data.settings import settings_manager

settings_manager.set('audio_format', 'mp3')
format = settings_manager.audio_format
```

#### 2. **history.py** - Verlaufs-Manager
- ✅ Download-History
- ✅ Automatische Speicherung
- ✅ Suche & Filter
- ✅ Statistiken

**Kern-Klasse:** `HistoryManager`

**Verwendung:**
```python
from mydownloader.data.history import history_manager

history_manager.add_entry(url, title, 'video', 'completed')
all_downloads = history_manager.get_all()
```

### Config-Module

#### **config.py** - Konfiguration
- ✅ Zentrale Konfiguration
- ✅ Settings-Wrapper
- ✅ Default-Values
- ✅ Property-Access

**Kern-Klasse:** `Config`

**Verwendung:**
```python
from mydownloader.config import config

config.download_folder = "/new/path"
config.save()
```

#### **constants.py** - Konstanten
- ✅ App-Konstanten
- ✅ Pfad-Definitionen
- ✅ Theme-Definitionen
- ✅ Status-Messages

## 🚀 Installation & Verwendung

### Entwicklungs-Modus

```bash
# 1. Repository klonen
git clone <repo-url>
cd MyDownloader

# 2. Virtual Environment erstellen (empfohlen)
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 3. Dependencies installieren
pip install -r requirements.txt

# 4. Anwendung starten
python -m mydownloader
# ODER direkt:
python app_tkinter_v3.py
```

### Production Build

```bash
# Windows
build.bat

# Erstellt:
# - dist/MyDownloader/MyDownloader.exe (Standalone)
# - dist/installer/MyDownloader-3.0.0-Setup.exe (Installer)
```

### Python Package Installation

```bash
# Lokale Installation
pip install -e .

# Dann startbar mit:
mydownloader
```

## 🔧 Build-Prozess

### 1. PyInstaller (Executable)

```bash
pyinstaller --name=MyDownloader \
    --onedir \
    --windowed \
    --icon=assets/icons/app_icon.ico \
    --add-data "assets;assets" \
    --hidden-import=PIL._tkinter_finder \
    --collect-all yt_dlp \
    mydownloader/__main__.py
```

**Output:** `dist/MyDownloader/MyDownloader.exe`

### 2. Inno Setup (Installer)

```bash
# Voraussetzung: Inno Setup 6.0+ installiert
# Download: https://jrsoftware.org/isinfo.php

"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" setup.iss
```

**Output:** `dist/installer/MyDownloader-3.0.0-Setup.exe`

### 3. Automatisch (build.bat)

```cmd
build.bat
```

Führt beide Schritte automatisch aus.

## 📋 Abhängigkeiten

### Kern-Dependencies
- **Python 3.8+**
- **yt-dlp**: YouTube Download
- **requests**: HTTP-Requests
- **Pillow**: Bildverarbeitung

### Optional
- **pyinstaller**: Executable-Erstellung
- **pytest**: Testing
- **black**: Code-Formatting

### System
- **FFmpeg**: Audio/Video-Verarbeitung (wird automatisch geladen)

## 🗂️ Daten-Speicherorte

### Benutzer-Daten
```
%USERPROFILE%\.mydownloader\
├── settings.json          # Benutzer-Einstellungen
├── history.json           # Download-Verlauf
└── app.log                # Anwendungs-Logs
```

### Downloads
```
Standardordner: %USERPROFILE%\Downloads\
Konfigurierbar in Einstellungen
```

### FFmpeg (Portable)
```
<App-Verzeichnis>\ffmpeg\bin\
├── ffmpeg.exe
├── ffprobe.exe
└── ffplay.exe
```

## 🏃 Entry Points

### 1. Direkter Start
```python
python app_tkinter_v3.py
```

### 2. Modul-Start
```python
python -m mydownloader
```

### 3. Installiertes Package
```bash
mydownloader         # Console
mydownloader-gui     # GUI (identisch)
```

### 4. Executable
```
MyDownloader.exe
```

## 🧪 Testing (geplant)

```bash
# Unit Tests
pytest tests/

# Mit Coverage
pytest --cov=mydownloader tests/

# Einzelner Test
pytest tests/test_downloader.py
```

## 📝 Code-Style (geplant)

```bash
# Formatting mit Black
black mydownloader/

# Linting mit Flake8
flake8 mydownloader/

# Type Checking mit MyPy
mypy mydownloader/
```

## 🔄 Update-Prozess

### yt-dlp Update
```python
from mydownloader.core.youtube import YouTubeDownloader

YouTubeDownloader.update_ytdlp()
```

### App-Update (zukünftig)
- Auto-Update-Funktion geplant
- Manuell: Neue Version installieren

## 🛠️ Konfiguration

### Programmatisch
```python
from mydownloader.config import config

config.set('audio_format', 'mp3')
config.set('download_folder', 'C:/Music')
config.save()
```

### Via GUI
Settings-Tab → Einstellungen ändern → Speichern

### Direkt (settings.json)
```json
{
    "download_folder": "C:/Music",
    "audio_format": "mp3",
    "theme": "dark",
    ...
}
```

## 🐛 Debugging

### Logs aktivieren
```python
from mydownloader.utils.logger import setup_logging
import logging

setup_logging(level=logging.DEBUG)
```

### Log-Datei
```
%USERPROFILE%\.mydownloader\app.log
```

### Verbose-Mode
```
# In-App: Logs-Fenster beobachten
# Terminal: Siehe Console-Output
```

## 🚧 Zukünftige Entwicklung

### Geplante Features (v3.1+)
- [ ] Vollständige GUI-Modularisierung (Tabs in separate Dateien)
- [ ] Unit Tests für alle Module
- [ ] Drag & Drop Support
- [ ] SponsorBlock Integration
- [ ] Video-Schnitt (Start/Ende)
- [ ] Auto-Update-Mechanismus
- [ ] Multi-Threading für Downloads
- [ ] Plugins-System

### Refactoring-Ideen
- [ ] GUI in separate Tab-Module aufteilen
- [ ] Custom Widgets extrahieren
- [ ] Theme-System erweitern
- [ ] Async/Await für Downloads
- [ ] Database statt JSON (SQLite)

## 📚 Weitere Dokumentation

- **README_V3.md**: Benutzer-Dokumentation
- **SCHNELLSTART_V3.md**: Quick Start Guide
- **FEATURE_VERGLEICH.md**: Feature-Übersicht v2 vs v3
- **PROJECT_STRUCTURE.md**: Diese Datei

## 💡 Best Practices

### Code-Organisation
- ✅ Ein Modul = Eine Verantwortlichkeit
- ✅ Klare Interfaces zwischen Modulen
- ✅ Logging in allen Modulen
- ✅ Error-Handling überall

### Performance
- ✅ Threading für UI-blockierende Operationen
- ✅ Queue-System für Batch-Downloads
- ✅ Lazy Loading wo möglich

### Sicherheit
- ✅ Input-Validierung
- ✅ Path-Traversal-Schutz
- ✅ Sichere Dateinamen
- ✅ Settings-Validierung

## 🙏 Credits

- **yt-dlp**: YouTube Download Engine
- **FFmpeg**: Audio/Video Processing
- **Python**: Programming Language
- **Tkinter**: GUI Framework
- **Inno Setup**: Windows Installer

---

**Version:** 3.0.0  
**Letzte Aktualisierung:** 2026-02-15  
**Autor:** UST-Germany
