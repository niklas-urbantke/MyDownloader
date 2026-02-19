# 🚀 SCHNELLSTART: Installer bauen

## In 3 Schritten zum fertigen Installer:

### 1️⃣ Inno Setup installieren (Optional, aber empfohlen)
- Download: https://jrsoftware.org/isdl.php
- Installiere die **Unicode-Version**
- Überspringen wenn du nur die .exe brauchst

### 2️⃣ Build starten
Doppelklick auf: **`build_setup_v3.bat`**

### 3️⃣ Warten
- Build dauert 3-10 Minuten
- **Nicht schließen!**
- Bei erstem Mal werden Dependencies installiert

## ✅ Fertig!

Deine Dateien sind im **`dist`** Ordner:
- **`MyDownloader.exe`** - Standalone (kann direkt verteilt werden)
- **`installer/MyDownloader-3.0.0-Setup.exe`** - Installer (nur wenn Inno Setup installiert)

## 📦 Was tun mit den Dateien?

### Für dich selbst:
- Starte einfach `dist/MyDownloader.exe`

### Zum Verteilen:
- **Einfach:** Schicke `MyDownloader.exe` per E-Mail/USB
- **Professionell:** Schicke `MyDownloader-3.0.0-Setup.exe`

## ❓ Probleme?

### Build schlägt fehl?
1. Stelle sicher Python ist installiert: `python --version`
2. Lies die komplette Anleitung: **BUILD_ANLEITUNG.md**

### Antivirus blockiert?
- Normal bei selbst-gebauten .exe Dateien
- Erstelle eine Ausnahme
- Optional: Code-Signierung (siehe BUILD_ANLEITUNG.md)

---

**Das war's! Viel Erfolg! 🎉**
