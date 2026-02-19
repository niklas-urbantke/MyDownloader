# 🎉 MyDownloader v3.0.0 - Major Release

**Ultimate Music & Video Downloader** für Windows 10/11

---

## 🚀 Highlights

- 🎨 **Komplettes UI-Redesign** - Modernes Windows 11-inspiriertes Design
- 📥 **Playlist-Download** - Ganze YouTube-Playlists herunterladen
- 📑 **Queue-System** - Mehrere Downloads nacheinander
- 🎵 **Mehr Formate** - MP3, M4A, FLAC, OPUS, WAV
- ⚙️ **Node.js Integration** - Behebt YouTube JavaScript-Warnungen
- 📊 **Download-History** - Behalte den Überblick
- 🌙 **Dark/Light Theme** - Wähle dein bevorzugtes Design
- 🔧 **Automatischer FFmpeg-Download** - Keine manuelle Installation!

## 📦 Download

**2 Versionen verfügbar:**

### ⭐ Windows Installer (Empfohlen für die meisten Nutzer)
- Datei: `MyDownloader-3.0.0-Setup.exe` 
- Größe: ~80 MB
- Professioneller Installationsassistent
- Start-Menü & Desktop-Icon
- Einfache Deinstallation

### 💾 Standalone Version (Portabel)
- Datei: `MyDownloader-v3.0.0-Standalone.zip`
- Größe: ~80 MB
- Keine Installation nötig
- Direkt ausführbar
- Perfekt für USB-Stick

## ⚡ Quick Start

1. Download & Installieren
2. URL einfügen (YouTube, etc.)
3. Format wählen (MP3, FLAC, ...)
4. Download starten! ✅

## 💻 Systemanforderungen

- Windows 10 (64-bit) oder neuer
- ~100 MB freier Speicherplatz
- Internetverbindung
- Optional: Node.js (für beste YouTube-Kompatibilität)

## 🆕 Was ist neu in v3.0.0

### Features
- ✅ Modernes Tab-Design (Download, Queue, History, Settings, Info)
- ✅ Video-Vorschau vor dem Download
- ✅ Batch-Import aus .txt Dateien
- ✅ Thumbnail & Metadaten-Einbettung
- ✅ Untertitel-Download (mehrere Sprachen)
- ✅ Geschwindigkeitslimit einstellbar
- ✅ Benutzerdef. Download-Ordner

### Verbesserungen
- ⚡ Schnellere Downloads
- 🎨 Bessere Benutzerführung
- 🔧 Stabilere Fehlerbehandlung
- 💾 Auto-Save für Einstellungen

### Bug Fixes
- 🐛 FFmpeg-Installation Probleme behoben
- 🐛 YouTube JavaScript-Runtime Warnung behoben
- 🐛 Playlist-Parsing verbessert
- 🐛 Encoding-Probleme mit Sonderzeichen behoben

## 🔧 Optional: Node.js für YouTube

Um die YouTube-Warnung zu beheben:

```bash
# Mit Chocolatey (empfohlen)
choco install nodejs

# Oder download von: https://nodejs.org
```

Dann in MyDownloader:
Einstellungen → Node.js Pfad → `C:\ProgramData\chocolatey\bin\node.exe`

## ⚠️ Windows Defender Warnung?

**Normal!** Die App ist nicht code-signiert. So beheben:
1. "Weitere Informationen" klicken
2. "Trotzdem ausführen" klicken
3. Oder: Ausnahme im Antivirus erstellen

Der Code ist 100% Open Source und sicher! ✅

## 📚 Dokumentation

- 📖 [Vollständige Release Notes](RELEASE_NOTES_v3.0.0.md)
- 🚀 [Schnellstart Guide](SCHNELLSTART_V3.md)
- 📘 [README](README_V3.md)
- 🔧 [Build Anleitung](BUILD_ANLEITUNG.md)

## 💬 Support & Feedback

- 🐛 Bugs melden: [Issues](https://github.com/yourusername/mydownloader/issues)
- 💡 Feature Requests: [Discussions](https://github.com/yourusername/mydownloader/discussions)
- ⭐ Gefällt's? Gib uns einen Stern!

## 🙏 Credits

Gebaut mit Python, tkinter, yt-dlp & FFmpeg

---

**Viel Spaß beim Downloaden! 🎵🎬**

Made with ❤️ by UST-Germany
