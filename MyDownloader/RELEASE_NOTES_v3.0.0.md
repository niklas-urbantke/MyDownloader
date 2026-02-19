# 🎉 MyDownloader v3.0.0 - Ultimate Music & Video Downloader

**Major Release** | Windows 10/11 | Stand-alone Installer verfügbar

---

## 🚀 Was ist neu?

MyDownloader v3.0.0 ist ein **komplettes Rewrite** der Anwendung mit moderner Benutzeroberfläche, erweiterten Features und verbesserter Stabilität!

### ✨ Neue Features

#### 🎨 Modernes UI/UX Design
- **Windows 11-inspiriertes Design** mit Dark/Light Theme
- **Tab-basierte Navigation** für bessere Übersichtlichkeit
- Moderne Farbpalette und verbesserte Typografie
- Responsive Design mit anpassbaren Fenstergrößen
- Hover-Effekte und sanfte Animationen

#### 📥 Download-Funktionen
- **Einzelvideo-Download** mit Vorschau-Funktion
- **Playlist-Download** - ganze YouTube-Playlists auf einmal
- **Queue-System** - mehrere Downloads nacheinander abarbeiten
- **Import aus Datei** oder Zwischenablage (.txt Listen)
- Automatisches Überspringen bereits heruntergeladener Dateien

#### 🎵 Audio-Formate
- **MP3** (Standard, beste Kompatibilität)
- **M4A** (Apple-Format, gute Qualität)
- **FLAC** (Verlustfrei, beste Qualität)
- **OPUS** (Modern, gute Kompression)
- **WAV** (Unkomprimiert)
- **Video-Download** (bestvideo+bestaudio)

#### ⚙️ Erweiterte Einstellungen
- **Qualitätsauswahl** (0-9, 0 = beste)
- **Thumbnail-Einbettung** in Audio-Dateien
- **Metadaten-Einbettung** (Künstler, Titel, etc.)
- **Untertitel-Download** (mehrere Sprachen)
- **Geschwindigkeitslimit** einstellbar
- **Benutzerdefinierbarer Download-Ordner**
- **Node.js Integration** für optimale YouTube-Unterstützung

#### 📊 History & Monitoring
- **Download-History** - behalte den Überblick
- **Echtzeit-Progress** mit Fortschrittsbalken
- **Detailliertes Logging** aller Aktivitäten
- Übersichtliche Tabellenansicht der Downloads

#### 🔧 Technische Verbesserungen
- **Automatischer FFmpeg-Download** - keine manuelle Installation nötig!
- **Portable FFmpeg** wird im App-Ordner installiert
- **yt-dlp Integration** mit automatischen Updates
- **Node.js Runtime-Konfiguration** behebt YouTube-Warnungen
- **Intelligente Fehlerbehandlung** und Retry-Mechanismus
- **Multi-Threading** für flüssige UI während Downloads

---

## 📦 Installation

### Windows Installer (Empfohlen)
1. Download: `MyDownloader-3.0.0-Setup.exe`
2. Doppelklick und Installationsassistent folgen
3. Optional: Desktop-Icon erstellen
4. Fertig! ✅

### Standalone Version
1. Download: `MyDownloader-v3.0.0-Standalone.zip`
2. Entpacken
3. `MyDownloader.exe` starten
4. Keine Installation nötig! ✅

---

## 💻 Systemanforderungen

**Minimum:**
- Windows 10 (64-bit) oder neuer
- 100 MB freier Speicherplatz
- Internetverbindung

**Empfohlen:**
- Windows 11 (64-bit)
- 200 MB freier Speicherplatz
- Node.js (für optimale YouTube-Unterstützung)
  - Installation: `choco install nodejs`
  - Oder von: https://nodejs.org

---

## 🎯 Quick Start

1. **Starte MyDownloader**
2. **Füge URL ein** (YouTube, etc.)
3. **Wähle Format** (MP3, M4A, FLAC, ...)
4. **Download starten!**

### Für Playlists:
1. Playlist-URL einfügen
2. "📋 Playlist laden" klicken
3. Vorschau prüfen
4. "▶️ Playlist Download starten"

### Für mehrere Videos:
1. Zum "📑 Queue" Tab wechseln
2. URLs importieren (Datei oder Zwischenablage)
3. "▶️ Queue starten"

---

## 🆕 Changelog v3.0.0

### Added
- ✅ Komplettes UI-Redesign mit modernem Look
- ✅ Tab-Navigation (Download, Queue, History, Settings, Info)
- ✅ Dark/Light Theme Support
- ✅ Video-Vorschau Funktion
- ✅ Queue-System mit Import-Funktion
- ✅ Download-History mit Tabellenansicht
- ✅ Node.js Runtime-Konfiguration
- ✅ Automatischer FFmpeg-Download
- ✅ Erweiterte Audio-Format-Unterstützung (FLAC, OPUS, WAV)
- ✅ Thumbnail & Metadaten-Einbettung
- ✅ Untertitel-Download
- ✅ Geschwindigkeitslimit-Einstellung
- ✅ Multi-Threading für bessere Performance
- ✅ Intelligentes Überspringen bereits vorhandener Dateien

### Improved
- ⚡ Schnellere Download-Geschwindigkeit
- 🎨 Bessere Benutzerführung
- 📊 Übersichtlichere Progress-Anzeige
- 🔧 Stabilere Fehlerbehandlung
- 💾 Automatisches Speichern der Einstellungen
- 🌍 Bessere Internationalisierung (DE/EN)

### Fixed
- 🐛 FFmpeg-Installation auf verschiedenen Systemen
- 🐛 YouTube-Download-Probleme mit JavaScript-Runtime
- 🐛 Playlist-Parsing-Fehler
- 🐛 Encoding-Probleme bei Dateinamen
- 🐛 Memory-Leaks bei langen Downloads

---

## 🔐 Sicherheit

Diese Version wurde mit PyInstaller gepackt und enthält:
- ✅ Keine schädlichen Komponenten
- ✅ Open-Source Code (siehe Repository)
- ✅ Keine Telemetrie oder Tracking
- ✅ Keine versteckten Downloads

**Windows Defender/Antivirus Warnung?**
- Normal bei selbst-kompilierten Anwendungen
- Code ist 100% sicher (siehe Source Code)
- Erstelle eine Ausnahme in deinem Antivirus

---

## 📚 Dokumentation

- **Schnellstart:** Siehe `SCHNELLSTART_V3.md`
- **Features:** Siehe `README_V3.md`
- **Build-Anleitung:** Siehe `BUILD_ANLEITUNG.md`
- **Problemlösung:** Siehe Issues oder Wiki

---

## 🛠️ Bekannte Probleme

### Windows Defender SmartScreen Warnung
**Problem:** "Windows hat Ihren PC geschützt" Warnung beim ersten Start  
**Lösung:** 
1. Klicke auf "Weitere Informationen"
2. Klicke auf "Trotzdem ausführen"
3. Dies ist normal bei nicht-signierten Anwendungen

### Node.js JavaScript Runtime Warnung
**Problem:** `WARNING: [youtube] No supported JavaScript runtime could be found`  
**Lösung:**
1. Node.js installieren: `choco install nodejs`
2. In MyDownloader: Einstellungen → Node.js Pfad konfigurieren
3. Standard: `C:\ProgramData\chocolatey\bin\node.exe`
4. Einstellungen speichern

### FFmpeg nicht gefunden
**Problem:** FFmpeg-Fehler beim Download  
**Lösung:** Wird automatisch behoben! Die App lädt FFmpeg automatisch herunter beim ersten Start.

---

## 🤝 Mitwirken

Contributions sind willkommen! 

- 🐛 **Bug Reports:** Erstelle ein Issue
- 💡 **Feature Requests:** Erstelle ein Issue mit "Feature Request" Label
- 🔧 **Pull Requests:** Gerne! Bitte `develop` Branch verwenden

---

## 📜 Lizenz

MIT License - Siehe `LICENSE` Datei

---

## 🙏 Credits

Gebaut mit:
- **Python 3.x** - Programmiersprache
- **tkinter** - GUI Framework
- **yt-dlp** - YouTube Download Engine
- **FFmpeg** - Media Verarbeitung
- **Pillow (PIL)** - Bildverarbeitung
- **PyInstaller** - Exe-Kompilierung
- **Inno Setup** - Windows Installer

Besonderer Dank an:
- yt-dlp Team für das großartige Tool
- FFmpeg Entwickler
- Python Community

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/yourusername/mydownloader/issues)
- **Discussions:** [GitHub Discussions](https://github.com/yourusername/mydownloader/discussions)
- **E-Mail:** support@ust-germany.de

---

## 🎉 Danke!

Danke fürs Nutzen von MyDownloader! Wenn dir die App gefällt:
- ⭐ **Gib uns einen Stern** auf GitHub
- 🐛 **Melde Bugs** wenn du welche findest
- 💡 **Teile deine Ideen** für neue Features
- 📢 **Empfehle uns weiter** an Freunde

**Viel Spaß beim Downloaden! 🎵🎬**

---

<div align="center">
Made with ❤️ by UST-Germany | Windows 10/11 | Version 3.0.0 | 2026
</div>
