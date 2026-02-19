# 🔧 Build-Anleitung für MyDownloader V3 Setup

Diese Anleitung erklärt, wie du einen standalone Windows-Installer für MyDownloader V3 erstellen kannst.

## 📋 Voraussetzungen

### Erforderlich:
1. **Python 3.8 oder neuer**
   - Download: https://www.python.org/downloads/
   - Bei Installation "Add Python to PATH" aktivieren!

2. **Virtual Environment** (empfohlen)
   - Sollte bereits vorhanden sein im Projekt

### Optional (für vollständigen Installer):
3. **Inno Setup 6**
   - Download: https://jrsoftware.org/isdl.php
   - Installiere die Unicode-Version
   - Standard-Installationspfad: `C:\Program Files (x86)\Inno Setup 6\`

## 🚀 Schnellstart

### Methode 1: Mit Batch-Datei (Einfachste Methode)

1. Öffne ein Terminal/CMD im `MyDownloader` Ordner
2. Führe aus:
   ```batch
   build_setup_v3.bat
   ```
3. Warte bis der Build abgeschlossen ist
4. Fertig! Die Dateien sind im `dist` Ordner

### Methode 2: Mit Python-Script (Mehr Kontrolle)

1. Öffne ein Terminal/CMD im `MyDownloader` Ordner
2. Aktiviere Virtual Environment (falls vorhanden):
   ```batch
   ..\.venv\Scripts\activate
   ```
3. Führe Build-Script aus:
   ```powershell
   python build_installer_v3.py
   ```
4. Warte bis der Build abgeschlossen ist
5. Fertig! Die Dateien sind im `dist` Ordner

## 📦 Was wird erstellt?

Nach erfolgreichem Build findest du folgende Dateien:

```
MyDownloader/
├── dist/
│   ├── MyDownloader.exe          ← Standalone .exe (kann direkt ausgeführt werden)
│   ├── README.txt                ← Informationen
│   └── installer/
│       └── MyDownloader-3.0.0-Setup.exe  ← Windows Installer (nur wenn Inno Setup installiert)
```

### 📄 MyDownloader.exe (Standalone)
- Größe: ~70-100 MB
- Benötigt **keine Installation**
- Kann direkt ausgeführt werden
- Alle Dependencies sind eingebettet
- Perfekt zum Verteilen als einzelne Datei

### 📦 MyDownloader-3.0.0-Setup.exe (Installer)
- Größe: ~70-100 MB
- Professioneller Windows-Installer
- Erstellt Start-Menü-Einträge
- Deinstallation über Systemsteuerung möglich
- Perfekt für professionelle Distribution

## 🔍 Detaillierter Build-Prozess

Der Build-Prozess besteht aus folgenden Schritten:

### Schritt 1: Aufräumen
- Löscht alte Build-Artefakte
- Entfernt `build/`, `dist/`, `__pycache__/`
- Löscht alte `.spec` Dateien

### Schritt 2: Dependencies installieren
- Installiert/Aktualisiert: `pyinstaller`, `pillow`, `yt-dlp`
- Alle anderen Dependencies sollten bereits installiert sein

### Schritt 3: Icon erstellen
- Prüft ob `assets/icon.ico` vorhanden ist
- Erstellt automatisch ein Standard-Icon falls nicht vorhanden
- Icon-Größen: 256x256, 128x128, 64x64, 32x32, 16x16

### Schritt 4: .exe bauen mit PyInstaller
- Kompiliert `app_tkinter_v3.py` zu einer .exe
- Einbettung aller Dependencies (yt-dlp, tkinter, PIL, etc.)
- `--onefile`: Alles in eine Datei
- `--windowed`: Kein Konsolen-Fenster
- Dauer: 2-5 Minuten je nach System

### Schritt 5: Installer-Dateien erstellen
- Erstellt README.txt mit Informationen
- Bereitet Dateien für Inno Setup vor

### Schritt 6 & 7: Windows Installer (Optional)
- Nur wenn Inno Setup installiert ist
- Verwendet `setup_v3.iss` Konfiguration
- Erstellt professionellen Installer mit:
  - Willkommens-Bildschirm
  - Lizenz-Anzeige
  - Installationspfad-Auswahl
  - Desktop-Icon Option
  - Deinstallations-Routine
  - Node.js-Hinweis

## ⚙️ Anpassungen

### Icon ändern
1. Erstelle ein Icon (256x256 PNG oder ICO)
2. Speichere es als `MyDownloader/assets/icon.ico`
3. Führe Build erneut aus

### Version ändern
In `build_installer_v3.py`:
```python
APP_VERSION = "3.0.0"  # Hier ändern
```

In `setup_v3.iss`:
```inno
#define MyAppVersion "3.0.0"  ; Hier ändern
```

### App-Name ändern
In `build_installer_v3.py`:
```python
APP_NAME = "MyDownloader"  # Hier ändern
```

## 🐛 Problemlösung

### Problem: "Python nicht gefunden"
**Lösung:**
1. Prüfe Python-Installation: `python --version`
2. Stelle sicher, dass Python im PATH ist
3. Neustart des Terminals

### Problem: "pyinstaller: command not found"
**Lösung:**
```powershell
pip install pyinstaller
```

### Problem: ".exe startet nicht"
**Lösung:**
1. Prüfe Windows Defender / Antivirus
2. Erstelle Ausnahme für die .exe
3. Führe Build-Script mit Administrator-Rechten aus

### Problem: "Inno Setup nicht gefunden"
**Lösung:**
- Das ist optional! Die standalone .exe wird trotzdem erstellt
- Wenn du den Installer brauchst:
  1. Installiere Inno Setup von https://jrsoftware.org/isdl.php
  2. Führ Build erneut aus

### Problem: "ImportError: PIL._tkinter_finder"
**Lösung:**
```powershell
pip install --upgrade Pillow
```

### Problem: Build dauert sehr lange
**Lösung:**
- Das ist normal! PyInstaller benötigt 2-5 Minuten
- Bei langsamen Systemen auch bis zu 10 Minuten
- Antivirus kann das verlangsamen (temporär deaktivieren)

## 📊 Build-Zeiten (Richtwerte)

| Hardware | .exe Build | Installer | Gesamt |
|----------|-----------|-----------|---------|
| Modern (i7, SSD) | 2-3 Min | 30 Sek | ~3 Min |
| Mittel (i5, HDD) | 4-6 Min | 1 Min | ~6 Min |
| Langsam (i3, HDD) | 8-10 Min | 2 Min | ~11 Min |

## 🎯 Tipps für Distribution

### Für Freunde/Familie:
- Verwende **MyDownloader.exe** (Standalone)
- Einfach per E-Mail oder USB-Stick verteilen
- Keine Installation nötig

### Für professionelle Distribution:
- Verwende **MyDownloader-Setup.exe** (Installer)
- Professioneller Eindruck
- Einfache Deinstallation
- Start-Menü Integration

### Für GitHub Release:
1. Erstelle beide Dateien
2. Packe standalone .exe in ZIP: `MyDownloader-v3.0.0-Standalone.zip`
3. Lade beide hoch:
   - `MyDownloader-v3.0.0-Standalone.zip`
   - `MyDownloader-3.0.0-Setup.exe`

## 📝 Checkliste vor Distribution

- [ ] Build erfolgreich abgeschlossen
- [ ] .exe auf eigenem System getestet
- [ ] .exe auf anderem Windows-PC getestet
- [ ] Alle Features funktionieren
- [ ] FFmpeg-Download funktioniert
- [ ] Node.js-Pfad konfigurierbar
- [ ] Einstellungen werden gespeichert
- [ ] README.txt aktuell
- [ ] Version korrekt in allen Dateien

## 🔐 Code-Signierung (Optional, Fortgeschritten)

Für professionelle Distribution solltest du die .exe signieren:

1. **Code-Signing Zertifikat besorgen**
   - Von DigiCert, Sectigo, GlobalSign, etc.
   - Kosten: ~200-500€ pro Jahr

2. **Signieren mit signtool.exe**
   ```batch
   signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com MyDownloader.exe
   ```

3. **Vorteile:**
   - Kein "Unbekannter Herausgeber" Warning
   - Windows SmartScreen vertraut der App
   - Professioneller Eindruck

## 🆘 Support

Bei Problemen:
1. Prüfe diese Anleitung
2. Lies die Fehlermeldung genau
3. Google die Fehlermeldung + "pyinstaller"
4. Erstelle ein GitHub Issue mit:
   - Fehlermeldung
   - Python-Version
   - Windows-Version
   - Build-Log

## 📚 Weiterführende Links

- [PyInstaller Doku](https://pyinstaller.org/en/stable/)
- [Inno Setup Doku](https://jrsoftware.org/ishelp/)
- [Python Packaging Guide](https://packaging.python.org/)
- [Windows Code Signing](https://docs.microsoft.com/en-us/windows/win32/seccrypto/cryptography-tools)

---

**Viel Erfolg beim Bauen deines Installers! 🚀**
