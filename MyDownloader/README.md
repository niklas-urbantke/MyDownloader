# 🎵 MyDownloader v3.0 - Ultimate Music & Video Downloader

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)]()

![MyDownloader Banner](assets/images/banner.png)

> **Professioneller YouTube Downloader mit moderner GUI und umfangreichen Features**

---

## 📑 Inhaltsverzeichnis

- [Features](#-features)
- [Installation](#-installation)
- [Schnellstart](#-schnellstart)
- [Dokumentation](#-dokumentation)
- [Projekt-Struktur](#-projekt-struktur)
- [Build & Distribution](#-build--distribution)
- [Entwicklung](#-entwicklung)
- [FAQ](#-faq)
- [Lizenz](#-lizenz)

---

## ✨ Features

### 🎯 Download-Modi
- ✅ **Einzelne Videos/Songs** herunterladen
- ✅ **Komplette Playlists** mit einem Klick
- ✅ **Queue-System** für Batch-Downloads
- ✅ **Batch-Import** aus Textdatei oder Zwischenablage

### 🎵 Audio-Formate
- MP3, M4A, OPUS, FLAC, WAV
- Qualitätsstufen: 0 (beste) bis 9 (kleinste Datei)
- Thumbnail als Cover-Art einbetten
- ID3-Metadaten automatisch

### 🎨 Moderne GUI
- Tab-basierte Navigation (Download, Queue, History, Settings, Info)
- Windows-Style Progressbar
- Dark/Light Theme
- Echtzeit-Logging
- Drag & Drop (geplant)

### ⚙️ Erweiterte Optionen
- Untertitel-Download (mehrere Sprachen)
- Geschwindigkeitslimit einstellbar
- Download-Ordner frei wählbar
- FFmpeg Auto-Installation
- yt-dlp Auto-Update

### 📊 Verwaltung
- Download-History (bis 100 Einträge)
- Einstellungen persistent (JSON)
- Import/Export von Einstellungen
- Statistiken & Verlauf

---

## 🚀 Installation

### Voraussetzungen:
- **Windows 10/11** (8 funktioniert auch)
- **Python 3.8+** ([Download](https://www.python.org/downloads/))
- **FFmpeg** (wird automatisch heruntergeladen)

### Methode 1: Direkt ausführen (Empfohlen für Entwicklung)

```bash
# 1. Repository öffnen
cd MyDownloader

# 2. Dependencies installieren
pip install -r requirements.txt

# 3. Starten
python app_tkinter_v3.py
```

### Methode 2: Als Python-Package

```bash
# Installation
pip install -e .

# Starten
mydownloader
```

### Methode 3: Windows Installer (Empfohlen für End-User)

```bash
# Installer erstellen
.\build.bat

# Dann: dist\installer\MyDownloader-3.0.0-Setup.exe installieren
```

📖 **Detaillierte Anleitung:** [INSTALLATION.md](INSTALLATION.md)

---

## ⚡ Schnellstart

### 1. Einzelnes Video herunterladen:
1. YouTube-URL kopieren
2. In App einfügen
3. "📥 Einzeln Download" klicken
4. Fertig! (Datei in Downloads-Ordner)

### 2. Playlist herunterladen:
1. Playlist-URL eingeben
2. "📋 Playlist laden" klicken
3. Vorschau prüfen
4. "▶️ Playlist Download starten" klicken

### 3. Batch-Download (Queue):
1. URLs einzeln zur Queue hinzufügen **ODER**
2. Aus Textdatei importieren **ODER**
3. Aus Zwischenablage einfügen
4. Tab "📑 Queue" öffnen
5. "▶️ Queue starten" klicken

📖 **Mehr Beispiele:** [SCHNELLSTART_V3.md](SCHNELLSTART_V3.md)

---

## 📚 Dokumentation

| Dokument | Beschreibung |
|----------|--------------|
| [README_V3.md](README_V3.md) | Ausführliches Benutzer-Handbuch |
| [SCHNELLSTART_V3.md](SCHNELLSTART_V3.md) | Quick Start Guide mit Beispielen |
| [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) | Projekt-Architektur & Module |
| [INSTALLATION.md](INSTALLATION.md) | Build & Installation-Anleitung |
| [FEATURE_VERGLEICH.md](FEATURE_VERGLEICH.md) | Feature-Übersicht v2 vs v3 |
| [ZUSAMMENFASSUNG.md](ZUSAMMENFASSUNG.md) | Projekt-Zusammenfassung |

---

## 🏗️ Projekt-Struktur

```
MyDownloader/
├── 📦 mydownloader/           # Haupt-Package
│   ├── core/                  # Download-Logik
│   │   ├── ffmpeg.py         # FFmpeg Manager
│   │   ├── youtube.py        # YouTube API
│   │   ├── downloader.py     # Download Engine
│   │   └── queue_manager.py  # Queue System
│   ├── gui/                   # Benutzeroberfläche
│   ├── utils/                 # Hilfsfunktionen
│   ├── data/                  # Daten-Management
│   └── config.py             # Konfiguration
│
├── 🔧 Setup & Build
│   ├── setup.py              # Python Package Setup
│   ├── setup.iss             # Windows Installer
│   ├── build.bat             # Build-Script
│   └── requirements.txt      # Dependencies
│
├── 📚 Dokumentation
│   ├── README.md             # Dieses Dokument
│   ├── README_V3.md          # Benutzer-Handbuch
│   ├── INSTALLATION.md       # Build-Anleitung
│   └── ...
│
└── 🎨 Assets
    ├── icons/                # App-Icons
    └── images/               # Bilder
```

📖 **Detailliert:** [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

---

## 🔨 Build & Distribution

### Executable erstellen (PyInstaller):

```bash
pyinstaller --name=MyDownloader \
    --onedir \
    --windowed \
    --icon=assets\icons\app_icon.ico \
    mydownloader\__main__.py
```

### Windows Installer (Inno Setup):

```bash
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" setup.iss
```

### Automatisch:

```bash
.\build.bat
```

**Output:**
- `dist\MyDownloader\MyDownloader.exe` (Standalone)
- `dist\installer\MyDownloader-3.0.0-Setup.exe` (Installer)

📖 **Detailliert:** [INSTALLATION.md](INSTALLATION.md#build--distribution)

---

## 💻 Entwicklung

### Repository klonen:

```bash
git clone <repository-url>
cd MyDownloader
```

### Virtual Environment (Empfohlen):

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Entwickeln:

```python
# App starten
python app_tkinter_v3.py

# Package als Modul
python -m mydownloader
```

### Testen (optional):

```bash
pytest tests/
pytest --cov=mydownloader tests/
```

### Code-Style (optional):

```bash
black mydownloader/
flake8 mydownloader/
mypy mydownloader/
```

---

## 🎯 Verwendungs-Beispiele

### Als Bibliothek verwenden:

```python
from mydownloader.core.downloader import downloader
from mydownloader.config import config

# Einfacher Download
success = downloader.download(
    url="https://youtube.com/watch?v=...",
    output_dir="C:/Music",
    settings=config.get_all()
)

# Queue verwenden
from mydownloader.core.queue_manager import queue_manager

queue_manager.add("url1")
queue_manager.add("url2")
queue_manager.start_processing("C:/Music", config.get_all())

# Video-Info abrufen
from mydownloader.core.youtube import youtube_downloader

info = youtube_downloader.get_video_info(url)
print(f"Titel: {info['title']}, Dauer: {info['duration']}s")
```

---

## ❓ FAQ

### **Q: FFmpeg nicht gefunden?**
**A:** Die App lädt FFmpeg automatisch beim ersten Start herunter (ca. 75 MB). Dauert 1-2 Minuten.

### **Q: Download schlägt fehl?**
**A:** 
1. yt-dlp aktualisieren (Einstellungen → "yt-dlp aktualisieren")
2. Internet-Verbindung prüfen
3. URL ist gültig und nicht privat/gelöscht

### **Q: Wo werden Dateien gespeichert?**
**A:** Standard: `%USERPROFILE%\Downloads\`. Änderbar in Einstellungen → Download-Ordner.

### **Q: Einstellungen gehen verloren?**
**A:** Einstellungen werden in `%USERPROFILE%\.mydownloader\settings.json` gespeichert. Nach Änderungen "Einstellungen speichern" klicken.

### **Q: Kein Sound/Video beschädigt?**
**A:** FFmpeg-Problem. Starte App neu, FFmpeg wird neu geladen.

### **Q: Langsame Downloads?**
**A:** 
- Einstellungen → Geschwindigkeitslimit entfernen (leer lassen)
- Format: MP3 statt FLAC für kleinere Dateien

📖 **Mehr FAQ:** [README_V3.md#troubleshooting](README_V3.md)

---

## 📊 Technische Details

### Architektur:
- **Pattern**: Modular, Manager-Pattern, Singleton
- **Threading**: Thread-safe Queue-System
- **Logging**: Rotating File Handler
- **Config**: JSON-basiert mit Validation
- **Error-Handling**: Comprehensive Try-Catch

### Dependencies:
- **yt-dlp**: YouTube Download Engine
- **Pillow**: Image Processing
- **requests**: HTTP Library
- **tkinter**: GUI Framework (built-in)

### Performance:
- **Startup**: ~2-3 Sekunden
- **Download**: Abhängig von Internet & Video-Größe
- **Memory**: ~50-100 MB während Download
- **Disk**: Settings ~1 KB, FFmpeg ~100 MB

---

## 🔐 Sicherheit

- ✅ Input-Validierung für alle URLs
- ✅ Path-Traversal-Protection
- ✅ Sichere Dateinamen (Sanitization)
- ✅ Keine externe Code-Ausführung
- ✅ Lokale Daten-Speicherung

---

## 🚀 Roadmap

### Version 3.1 (geplant):
- [ ] Drag & Drop für URLs
- [ ] Thumbnail-Vorschau in GUI
- [ ] SponsorBlock Integration
- [ ] Video-Schnitt (Start/Ende)
- [ ] Playlist-Sortierung

### Version 3.2 (geplant):
- [ ] Proxy & Cookies Support
- [ ] Multi-Threading für Downloads
- [ ] Tray-Icon & Background-Mode
- [ ] Auto-Update für App selbst
- [ ] Download-Statistiken

### Future:
- [ ] Linux/Mac Support
- [ ] Spotify Integration
- [ ] Plugins-System
- [ ] Web-Interface (optional)

---

## 🤝 Contributing

Contributions sind willkommen! 

1. Fork das Repository
2. Erstelle einen Feature-Branch (`git checkout -b feature/AmazingFeature`)
3. Commit deine Änderungen (`git commit -m 'Add AmazingFeature'`)
4. Push zum Branch (`git push origin feature/AmazingFeature`)
5. Öffne einen Pull Request

### Code-Style:
- Python 3.8+ Type Hints
- Docstrings für alle Funktionen
- Black Formatting
- Aussagekräftige Commit-Messages

---

## 📄 Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert - siehe [LICENSE](LICENSE) für Details.

### Third-Party:
- **yt-dlp**: Public Domain / Unlicense
- **FFmpeg**: LGPL v2.1+ / GPL v2+
- **Python**: PSF License

---

## 🙏 Credits & Thanks

- **yt-dlp Team**: Für die exzellente YouTube-Download-Library
- **FFmpeg**: Für die universelle Multimedia-Verarbeitung
- **Python Community**: Für Tkinter und alle Libraries

---

## 💬 Support & Contact

- **Issues**: [GitHub Issues](https://github.com/yourusername/mydownloader/issues)
- **Dokumentation**: Diese README & Docs-Ordner
- **Email**: your.email@example.com

---

## 📸 Screenshots

### Main Window
![Main Window](assets/images/screenshots/main_window.png)

### Download Tab
![Download Tab](assets/images/screenshots/download_tab.png)

### Settings
![Settings](assets/images/screenshots/settings_tab.png)

---

## ⭐ Show Your Support

Gefällt dir das Projekt? Gib einen ⭐️!

---

<div align="center">

**Made with ❤️ using Python, yt-dlp & FFmpeg**

[📥 Download](https://github.com/yourusername/mydownloader/releases) • 
[📚 Docs](README_V3.md) • 
[🐛 Report Bug](https://github.com/yourusername/mydownloader/issues) • 
[✨ Request Feature](https://github.com/yourusername/mydownloader/issues)

---

**MyDownloader v3.0** | © 2026 UST-Germany | MIT License

</div>
