# 📦 MyDownloader - Installations- & Build-Anleitung

## 🎯 Übersicht

MyDownloader kann auf drei Arten verwendet werden:
1. **Direkt ausführen** (Entwicklung/Testing)
2. **Als Python-Package installieren**
3. **Windows Installer erstellen** (für Distribution)

---

## 🚀 Methode 1: Direkt ausführen (Schnellst)

### Voraussetzungen:
- Python 3.8 oder höher
- pip
- Git (optional)

### Schritte:

```bash
# 1. Projekt-Ordner öffnen
cd "C:\...\MyDownloader"

# 2. Dependencies installieren
pip install -r requirements.txt

# 3. Anwendung starten
python app_tkinter_v3.py
```

**Fertig!** Die Anwendung sollte sich öffnen.

### Troubleshooting:
```bash
# Wenn Python nicht gefunden wird:
where python
# Sollte Python-Pfad anzeigen

# Wenn pip Fehler wirft:
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

---

## 📦 Methode 2: Als Package installieren

### Development Installation:

```bash
# 1. In Projekt-Ordner wechseln
cd "C:\...\MyDownloader"

# 2. Editable Install (Änderungen wirken sofort)
pip install -e .

# 3. Starten
mydownloader
# ODER
python -m mydownloader
```

### Production Installation:

```bash
# 1. Package bauen
python setup.py sdist bdist_wheel

# 2. Installieren
pip install dist/mydownloader-3.0.0-py3-none-any.whl

# 3. Starten
mydownloader
```

### Deinstallation:

```bash
pip uninstall mydownloader
```

---

## 🔨 Methode 3: Windows Installer erstellen

### Voraussetzungen:

#### 1. Python & Dependencies
```bash
python --version  # Sollte 3.8+ sein
pip install -r requirements.txt
pip install pyinstaller
```

#### 2. Inno Setup (für Installer)
- Download: https://jrsoftware.org/isinfo.php
- Version: 6.0 oder höher
- Standard-Installation durchführen

### Build-Prozess:

#### Option A: Automatisches Build-Script (Empfohlen)

```cmd
# Einfach Doppelklick auf:
build.bat

# ODER im Terminal:
.\build.bat
```

Das Script wird:
1. ✅ Dependencies prüfen
2. ✅ PyInstaller ausführen
3. ✅ Executable erstellen
4. ✅ Inno Setup Installer bauen

**Output:**
- `dist\MyDownloader\MyDownloader.exe` (Standalone)
- `dist\installer\MyDownloader-3.0.0-Setup.exe` (Installer)

#### Option B: Manuell

##### Schritt 1: Executable mit PyInstaller

```bash
pyinstaller --name=MyDownloader ^
    --onedir ^
    --windowed ^
    --icon=assets\icons\app_icon.ico ^
    --add-data "assets;assets" ^
    --hidden-import=PIL._tkinter_finder ^
    --collect-all yt_dlp ^
    --noconfirm ^
    mydownloader\__main__.py
```

##### Schritt 2: Installer mit Inno Setup

```bash
# Inno Setup Compiler ausführen
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" setup.iss
```

### Ausgabe-Dateien:

```
dist/
├── MyDownloader/               # Portable Version
│   ├── MyDownloader.exe       # Haupt-Executable
│   ├── _internal/             # Dependencies
│   └── ...
│
└── installer/
    └── MyDownloader-3.0.0-Setup.exe  # Windows Installer
```

### Testen des Builds:

```bash
# 1. Standalone testen
cd dist\MyDownloader
MyDownloader.exe

# 2. Installer testen
cd dist\installer
# Doppelklick auf MyDownloader-3.0.0-Setup.exe
```

---

## 🎨 Optional: Icon erstellen

Falls du ein eigenes Icon möchtest:

### Icon-Anforderungen:
- Format: `.ico`
- Größen: 16x16, 32x32, 48x48, 256x256
- Speicherort: `assets/icons/app_icon.ico`

### Icon erstellen:

#### Online:
1. Gehe zu https://convertio.co/png-ico/
2. Lade PNG hoch (256x256 empfohlen)
3. Konvertiere zu ICO
4. Speichere als `app_icon.ico`

#### Mit Python (PIL):
```python
from PIL import Image

# PNG zu ICO
img = Image.open('icon.png')
img.save('app_icon.ico', format='ICO', sizes=[(16,16), (32,32), (48,48), (256,256)])
```

#### Mit GIMP:
1. Öffne Bild in GIMP
2. Bild → Skalieren → 256x256
3. Datei → Exportieren als → .ico
4. Wähle: 16x16, 32x32, 48x48, 256x256

---

## 🔧 Build-Konfiguration anpassen

### PyInstaller-Optionen (in build.bat):

```bash
--name=MyDownloader              # Name der EXE
--onedir                         # Alles in einem Ordner (Alternative: --onefile)
--windowed                       # GUI-App (ohne Console)
--icon=assets\icons\app_icon.ico # Icon-Datei
--add-data "assets;assets"       # Assets mitpacken
--hidden-import=PIL._tkinter_finder  # Tkinter-Fix
--collect-all yt_dlp             # yt-dlp vollständig einbinden
--noconfirm                      # Überschreiben ohne Nachfrage
```

### Inno Setup-Optionen (in setup.iss):

```ini
AppName={#MyAppName}              ; App-Name
AppVersion={#MyAppVersion}        ; Version
DefaultDirName={autopf}\...       ; Standard-Installationsordner
SetupIconFile=...                 ; Installer-Icon
OutputBaseFilename=...            ; Name der Installer-EXE
Compression=lzma2/ultra64         ; Kompression
```

---

## 🌍 Virtual Environment (Empfohlen für Entwicklung)

### Creation:

```bash
# Erstellen
python -m venv venv

# Aktivieren (Windows)
venv\Scripts\activate

# Aktivieren (Linux/Mac)
source venv/bin/activate

# Dependencies installieren
pip install -r requirements.txt
```

### Verwendung:

```bash
# Immer zuerst aktivieren
venv\Scripts\activate

# Dann arbeiten
python app_tkinter_v3.py

# Deaktivieren
deactivate
```

---

## 📋 Checkliste vor Distribution

### Vor dem Build:

- [ ] Alle Dependencies in `requirements.txt`
- [ ] Version-Nummer aktualisiert (setup.py, setup.iss, constants.py)
- [ ] Icon vorhanden (`assets/icons/app_icon.ico`)
- [ ] README und Dokumentation aktuell
- [ ] Tests durchgeführt (wenn vorhanden)
- [ ] Code committet & gepusht (wenn Git verwendet)

### Nach dem Build:

- [ ] Executable getestet (dist\MyDownloader\MyDownloader.exe)
- [ ] Installer getestet (Installation + Deinstallation)
- [ ] FFmpeg-Auto-Download funktioniert
- [ ] Download-Test durchgeführt
- [ ] Einstellungen speichern/laden funktioniert
- [ ] Logs werden erstellt
- [ ] Kein Antivirus-False-Positive (VirusTotal-Check)

### Distribution:

- [ ] Installer umbenennen (z.B. `MyDownloader-v3.0.0-Setup.exe`)
- [ ] Checksumme erstellen (SHA256)
- [ ] Release auf GitHub/Platform
- [ ] Changelog beifügen
- [ ] Installationsanleitung verlinken

---

## 🐛 Troubleshooting

### PyInstaller-Fehler:

```bash
# "Module not found" Error:
# Lösung: Hidden import hinzufügen
--hidden-import=modulename

# "Failed to execute script":
# Lösung: --debug=all verwenden
pyinstaller --debug=all ...

# UPX Error:
# Lösung: UPX deaktivieren
--noupx
```

### Inno Setup-Fehler:

```bash
# "File not found":
# → Prüfe Pfade in setup.iss
# → Stelle sicher, dass PyInstaller erfolgreich war

# "Compiler not found":
# → Inno Setup korrekt installiert?
# → Pfad in build.bat prüfen
```

### Runtime-Fehler:

```bash
# "Python was not found":
# → Bei onedir: Python ist eingebettet
# → Bei onefile: Kann an fehlenden DLLs liegen

# "FFmpeg not available":
# → Normal beim ersten Start
# → App lädt FFmpeg automatisch

# "Settings not saved":
# → Prüfe Schreibrechte in %USERPROFILE%\.mydownloader
```

---

## 🚀 Automatisches Deployment (Zukünftig)

### GitHub Actions (geplant):

```yaml
name: Build Installer

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build with PyInstaller
        run: build.bat
      - name: Upload Installer
        uses: actions/upload-artifact@v2
        with:
          name: installer
          path: dist/installer/*.exe
```

---

## 💰 Build-Zeiten (Richtwerte)

- **PyInstaller**: ~2-5 Minuten
- **Inno Setup**: ~30 Sekunden
- **Gesamt**: ~3-6 Minuten

Abhängig von:
- CPU-Leistung
- Festplatten-Geschwindigkeit
- Antivirus-Scans

---

## 📞 Support

Bei Build-Problemen:

1. **Logs prüfen**: Siehe Terminal-Output
2. **Clean Build**: Lösche `build/` und `dist/` Ordner
3. **Dependencies**: `pip install --upgrade -r requirements.txt`
4. **Python-Version**: Mindestens 3.8
5. **Admin-Rechte**: Manchmal bei Writezugriff nötig

---

## 🎉 Fertig!

Nach erfolgreicher Installation solltest du haben:

- ✅ Lauffähige Standalone-Executable
- ✅ Professioneller Windows-Installer
- ✅ Deinstallations-Programm
- ✅ Start-Menu-Einträge
- ✅ Desktop-Icon (optional)

**Happy Developing & Distributing!** 🚀
