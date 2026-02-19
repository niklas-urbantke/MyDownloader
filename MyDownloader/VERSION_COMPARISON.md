# 🎵 MyDownloader - Versionsübersicht

Es gibt jetzt **zwei Versionen** von MyDownloader:

## 1. Python Version (Original)
📁 Ordner: `MyDownloader/` (Haupt-Ordner)

### ✅ Vorteile
- Schnelle Entwicklung und Anpassungen
- Einfache Installation (nur Python + pip)
- Kleinere Dateigröße
- Cross-platform ohne Neukompilierung

### ❌ Nachteile
- Benötigt Python-Installation
- Langsamerer Start
- Höherer Speicherverbrauch
- UI ist nicht vollständig nativ

### 🚀 Installation
```bash
pip install -r requirements.txt
python app_modern.py
```

---

## 2. C++ Version (Neu!)
📁 Ordner: `MyDownloader/cpp/`

### ✅ Vorteile
- **Native UI-Elemente** für jedes Betriebssystem:
  - Windows: Win32-Controls
  - macOS: Cocoa-Controls
  - Linux: GTK+-Controls
- Schnellerer Start
- Geringerer Speicherverbrauch
- Standalone-Executable (keine Python nötig)
- Bessere Performance

### ❌ Nachteile
- Komplexere Installation (Build-Tools nötig)
- Größere Executable
- Muss für jede Plattform kompiliert werden

### 🚀 Installation
Siehe [cpp/README.md](cpp/README.md) oder [cpp/QUICKSTART.md](cpp/QUICKSTART.md)

---

## Welche Version soll ich nutzen?

### Nutze die **Python Version**, wenn:
- ✅ Du Python bereits installiert hast
- ✅ Du schnell loslegen willst
- ✅ Du die Software anpassen möchtest
- ✅ Du kein Build-System installieren willst

### Nutze die **C++ Version**, wenn:
- ✅ Du native UI-Elemente bevorzugst
- ✅ Du bessere Performance willst
- ✅ Du Python nicht installieren möchtest
- ✅ Du eine Standalone-Anwendung willst
- ✅ Du mit C++ und CMake vertraut bist

---

## Feature-Vergleich

| Feature | Python | C++ |
|---------|--------|-----|
| Download von Videos/Musik | ✅ | ✅ |
| Playlist-Support | ✅ | ✅ |
| Queue-System | ✅ | ✅ |
| Download-History | ✅ | ✅ |
| Audio-Formate (MP3, M4A, etc.) | ✅ | ✅ |
| Qualitätseinstellungen | ✅ | ✅ |
| Thumbnail einbetten | ✅ | ✅ |
| Metadata einbetten | ✅ | ✅ |
| **Native UI-Elemente** | ❌ | ✅ |
| **Standalone Executable** | ❌ | ✅ |
| **Schneller Start** | ❌ | ✅ |
| **Weniger Speicher** | ❌ | ✅ |
| **Einfache Installation** | ✅ | ❌ |
| **Einfache Anpassung** | ✅ | ❌ |

---

## Screenshots

### Python Version (CustomTkinter)
- Moderne, thembare UI
- Dark/Light Mode
- Plattformübergreifend konsistent

### C++ Version (wxWidgets)
- **Windows**: Echte Windows-Buttons und -Controls
- **macOS**: Echte macOS Aqua-Controls
- **Linux**: Echte GTK+-Widgets
- Integriert sich perfekt ins Betriebssystem

---

## Technische Details

### Python Version
- **Framework**: CustomTkinter / Tkinter
- **Sprache**: Python 3.8+
- **Dependencies**: yt-dlp, customtkinter, etc.
- **Dateigröße**: ~50 KB (Python-Skripte)
- **Laufzeit**: Benötigt Python-Interpreter

### C++ Version
- **Framework**: wxWidgets 3.2+
- **Sprache**: C++17
- **Build-System**: CMake
- **Dependencies**: wxWidgets, nlohmann/json, cpr
- **Dateigröße**: ~5-15 MB (kompiliertes Binary)
- **Laufzeit**: Standalone, keine Dependencies zur Laufzeit

---

## Migration von Python zu C++

Die C++-Version verwendet die gleichen Backend-Tools (yt-dlp, FFmpeg), daher sind:
- ✅ Downloads kompatibel
- ✅ Einstellungen können übernommen werden (JSON-Format)
- ✅ History kann übernommen werden (JSON-Format)
- ✅ Alle Features sind vorhanden

Beide Versionen können parallel installiert sein!

---

## Entwicklung

### Python-Version entwickeln
```bash
cd MyDownloader
# Bearbeite .py Dateien
python app_modern.py
```

### C++-Version entwickeln
```bash
cd MyDownloader/cpp
# Bearbeite .cpp/.h Dateien
mkdir build && cd build
cmake ..
cmake --build .
```

---

## Support & Dokumentation

- **Python Version**: Siehe [README.md](README.md) und [SCHNELLSTART_V3.md](SCHNELLSTART_V3.md)
- **C++ Version**: Siehe [cpp/README.md](cpp/README.md) und [cpp/QUICKSTART.md](cpp/QUICKSTART.md)

---

## Lizenz

Beide Versionen sind unter der **MIT License** lizenziert.

**Viel Spaß mit MyDownloader! 🎵**

Choose your flavor: **Python** für Flexibilität oder **C++** für Performance! 🚀
