# 🎵 Ultimate Music & Video Downloader v3.0

Eine umfassende Desktop-Anwendung zum Herunterladen von Music und Videos von YouTube mit vielen Features!

## ✨ Hauptfeatures

### 📥 **Download-Modi**
- **Einzelne Videos/Songs** - Schnell einzelne Inhalte herunterladen
- **Komplette Playlists** - Ganze YouTube-Playlists auf einmal laden
- **Queue-System** - Mehrere Downloads in eine Warteschlange einreihen
- **Batch-Import** - URLs aus Textdateien oder Zwischenablage importieren

### 🎵 **Audio-Formate**
Unterstützt alle gängigen Audio-Formate:
- **MP3** - Standard-Format, überall abspielbar
- **M4A** - AAC-Format mit guter Qualität
- **OPUS** - Modernes Format mit hoher Effizienz
- **FLAC** - Verlustfreies Format für Audiophile
- **WAV** - Unkomprimiert für maximale Qualität
- **Video-Modus** - Behalte das Video (keine Audio-Extraktion)

### 🎨 **Benutzeroberfläche**
- **Tab-basierte Navigation** - Übersichtliche Organisation
  - 📥 Download - Haupt-Download-Bereich
  - 📑 Queue - Batch-Download-Verwaltung
  - 📜 History - Verlauf aller Downloads
  - ⚙️ Einstellungen - Umfangreiche Konfiguration
  - ℹ️ Info - Über die App
- **Windows-Style Progressbar** - Native Windows-Optik
- **Dark/Light Theme** - Wählbares Farbschema
- **Echtzeit-Logs** - Sehe genau, was passiert

### 👁️ **Vorschau-Funktion**
Vor dem Download:
- Titel und Uploader anzeigen
- Video-Dauer prüfen
- View-Count sehen
- Thumbnail ansehen (geplant)

### 📁 **Flexible Speicherung**
- **Ordner-Auswahl** - Wähle deinen Download-Ordner per Windows-Dialog
- **Einstellungen merken** - Letzter Ordner wird gespeichert
- **Automatische Organisation** - Playlists werden in Unterordnern gespeichert

### 🎛️ **Erweiterte Optionen**

#### Audio-Optimierung
- ✅ Thumbnail einbetten (Cover-Art)
- ✅ Metadaten einbetten (Titel, Künstler, etc.)
- ✅ Qualitätsstufen (0=Beste bis 9=Kleinste Datei)

#### Untertitel
- 💬 Untertitel herunterladen
- 🌍 Mehrere Sprachen gleichzeitig (z.B. "de,en,fr")
- 📄 Format: SRT (Standard-Untertitelformat)

#### Performance
- ⚡ **Geschwindigkeitslimit** - Schone deine Internetverbindung
- 🔄 **Auto-Update** - yt-dlp mit einem Klick aktualisieren
- ⏸️ **Abbrechen** - Downloads jederzeit stoppen

### 📊 **Download-History**
- Automatischer Verlauf aller Downloads
- Sortiert nach Datum/Zeit
- Titel und URL gespeichert
- Bis zu 100 letzte Einträge
- History-Export/Import (JSON)

### 📑 **Queue-System**

#### Import-Möglichkeiten:
1. **Einzeln hinzufügen** - Button "Zur Queue"
2. **Aus Datei** - TXT-Datei mit URLs (eine pro Zeile)
3. **Aus Zwischenablage** - URLs direkt aus Clipboard einfügen

#### Queue-Verwaltung:
- Liste aller wartenden Downloads
- Einzelne Einträge entfernen (Rechtsklick)
- Komplette Queue leeren
- Queue-Download starten

## 🚀 Installation

### Voraussetzungen:
```bash
pip install -r requirements.txt
```

**requirements.txt:**
```
tkinter (meist vorinstalliert)
yt-dlp
Pillow
requests
```

### FFmpeg:
Die App lädt FFmpeg automatisch herunter, wenn es nicht gefunden wird!

**Alternativ manuell installieren:**
- Windows: `winget install Gyan.FFmpeg`
- Oder von: https://ffmpeg.org/download.html

## 📖 Verwendung

### Start:
```bash
python app_tkinter_v3.py
```

### Workflows:

#### 1️⃣ Einzelner Song/Video:
1. URL eingeben
2. Optional: Vorschau anzeigen
3. "Einzeln Download" klicken
4. Fertig!

#### 2️⃣ Playlist herunterladen:
1. Playlist-URL eingeben
2. "Playlist laden" klicken
3. Vorschau prüfen
4. "Playlist Download starten" klicken
5. Fortschritt beobachten

#### 3️⃣ Batch-Download (Queue):
1. URLs einzeln hinzufügen oder aus Datei/Clipboard importieren
2. Zum Queue-Tab wechseln
3. Queue prüfen
4. "Queue starten" klicken
5. Alle Downloads werden nacheinander ausgeführt

## ⚙️ Einstellungen

### Audio-Einstellungen:
- **Format**: Wähle zwischen MP3, M4A, OPUS, FLAC, WAV oder Video
- **Qualität**: 0 (beste) bis 9 (kleinste Datei)
- **Thumbnail**: Als Cover-Art in Datei einbetten
- **Metadaten**: Titel, Künstler, Album automatisch eintragen

### Untertitel:
- **Download aktivieren**: Checkbox aktivieren
- **Sprachen**: Komma-getrennt (z.B. "de,en,pl")
- Format: Immer SRT (SubRip)

### Download:
- **Geschwindigkeitslimit**: In MB/s (leer = unbegrenzt)
- Verhindert Überlastung der Leitung

### Aussehen:
- **Theme**: Dark oder Light
- Neustart nach Änderung erforderlich

### Speichern:
- Klicke "Einstellungen speichern"
- Werden in `settings.json` gespeichert
- Beim nächsten Start automatisch geladen

## 📂 Datei-Struktur

```
Spotify Downloader/
├── app_tkinter_v3.py          # Haupt-Anwendung (NEU!)
├── app_tkinter_v2.py          # Alte Version
├── requirements.txt           # Python-Abhängigkeiten
├── settings.json              # Gespeicherte Einstellungen
├── download_history.json      # Download-Verlauf
├── ffmpeg/                    # Automatisch heruntergeladenes FFmpeg
│   └── bin/
│       ├── ffmpeg.exe
│       ├── ffprobe.exe
│       └── ffplay.exe
└── Songs/                     # Standard Download-Ordner
    ├── Playlist Name 1/
    │   ├── Artist - Song1.mp3
    │   └── Artist - Song2.mp3
    └── Playlist Name 2/
        └── ...
```

## 🔧 Troubleshooting

### FFmpeg nicht gefunden?
→ Die App lädt es automatisch! Falls nicht:
```bash
winget install Gyan.FFmpeg
```

### yt-dlp Fehler?
→ Klicke in Einstellungen auf "yt-dlp aktualisieren"

### Download schlägt fehl?
→ Prüfe:
1. Internet-Verbindung
2. URL ist gültig
3. Video ist nicht privat/gelöscht
4. FFmpeg ist verfügbar

### Langsame Downloads?
→ In Einstellungen:
- Geschwindigkeitslimit erhöhen/entfernen

### Keine Metadaten/Thumbnails?
→ In Einstellungen:
- "Thumbnail einbetten" aktivieren
- "Metadaten einbetten" aktivieren

## 🆕 Neu in Version 3.0

### Haupt-Features:
✅ **Tab-basierte GUI** - Übersichtliche Organisation
✅ **Download-Ordner Auswahl** - Windows-Dialog mit Speichern
✅ **Einzelsong-Download** - Direkter Download ohne Playlist
✅ **Queue-System** - Batch-Downloads verwalten
✅ **Vorschau-Funktion** - Vor Download prüfen
✅ **Download-History** - Automatischer Verlauf
✅ **Format-Auswahl** - MP3, M4A, FLAC, OPUS, WAV
✅ **Untertitel-Support** - Multiple Sprachen
✅ **Geschwindigkeitslimit** - Bandwidth-Kontrolle
✅ **Batch-Import** - Aus Datei & Zwischenablage
✅ **Windows-Style UI** - Native Optik
✅ **Dark/Light Theme** - Wählbar
✅ **Auto-Update** - yt-dlp mit einem Klick
✅ **Settings-Persistenz** - Einstellungen bleiben erhalten
✅ **Thumbnail-Embedding** - Cover-Art in Audiodateien
✅ **Metadata-Embedding** - Vollständige ID3-Tags

### UI-Verbesserungen:
- 📊 Windows-nativer Progressbar
- 🎨 Moderne Tab-Navigation
- 📝 Echtzeit-Logging
- 👁️ Vorschau vor Download
- 📁 Ordner-Dialog mit Windows-Look
- ⚙️ Umfangreiche Einstellungen

### Geplante Features (v3.1):
- 🖼️ Thumbnail-Vorschau in GUI
- 🎯 SponsorBlock Integration
- ✂️ Video-Schnitt (Start/Ende)
- 🔐 Proxy & Cookies Support
- 🎭 Drag & Drop für URLs
- 🔔 Tray-Icon & Background-Downloads
- 📊 Download-Statistiken
- 🎨 Custom Themes

## 💡 Tipps & Tricks

### Schnelle Downloads:
1. Format: MP3 oder M4A (FLAC ist größer)
2. Qualität: 2-5 (0 ist oft übertrieben)
3. Kein Geschwindigkeitslimit

### Beste Qualität:
1. Format: FLAC oder WAV
2. Qualität: 0
3. Thumbnail & Metadaten einbetten

### Für unterwegs:
1. Format: OPUS oder M4A
2. Qualität: 5-7 (kleiner, trotzdem gut)

### Playlists sortieren:
- Werden automatisch in Unterordnern gespeichert
- Format: "Artist - Title.mp3"

### Batch-Download:
1. URLs in Textdatei sammeln (eine pro Zeile)
2. "Aus Datei importieren"
3. Alles auf einmal laden!

### History nutzen:
- Finde alte Downloads schnell wieder
- URL kopieren für erneuten Download
- Als Backup der Downloads

## 📄 Lizenz

Dieses Projekt verwendet:
- **yt-dlp** - Public Domain / Unlicense
- **FFmpeg** - LGPL/GPL
- **Python** - PSF License

## 🤝 Credits

Erstellt mit:
- Python 3.x
- Tkinter (GUI)
- yt-dlp (YouTube Download)
- FFmpeg (Audio/Video Verarbeitung)
- Pillow (Bildverarbeitung)

## 📞 Support

Bei Problemen:
1. Prüfe diese README
2. Aktualisiere yt-dlp (Button in Einstellungen)
3. Prüfe FFmpeg-Installation
4. Logs in der GUI beachten

## 🎉 Viel Spaß beim Downloaden!

Made with ❤️ using Python
