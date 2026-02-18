# Music Playlist Downloader - Desktop App

Eine moderne Desktop-Anwendung mit Web-GUI zum Herunterladen von YouTube-Playlists als MP3-Dateien.

## Features

✨ **Desktop-App mit Tkinter Control Panel**
- Eigenständiges Windows-Fenster zur Steuerung
- Automatischer Browser-Start
- Server-Status-Anzeige
- Port-Verwaltung

🎨 **Moderne Web-Benutzeroberfläche**
- Ansprechendes, dunkles Design mit Spotify-inspirierter Farbgebung
- Responsive Design für Desktop und Mobile
- Echtzeit-Fortschrittsanzeige mit animierten Balken

🎵 **Intelligente Download-Funktion**
- Automatische Suche nach Album-Versionen (Topic Channels)
- Bevorzugung von "Official Audio" und "Provided to YouTube"
- Fallback auf Original-Playlist-Videos
- Dateiname-Format: "Künstler - Titel.mp3"

⚡ **Live-Updates**
- WebSocket-basierte Echtzeit-Kommunikation
- Live-Status für jeden einzelnen Song
- Visuelles Feedback für alle Prozesse

🔧 **Automatische FFmpeg-Installation**
- Automatische Erkennung von System-FFmpeg
- Download und Installation einer portablen Version bei Bedarf
- Keine manuelle Installation erforderlich

🔒 **Zuverlässig**
- Automatische Duplikatserkennung
- Fehlerbehandlung und Retry-Logik
- Dynamische Port-Auswahl (keine Konflikte)

## Installation

### Voraussetzungen

1. **Python 3.14+** (bereits installiert)
2. **FFmpeg** (bereits installiert via winget)
3. **Virtual Environment** (bereits aktiviert)

### Pakete installieren

Die erforderlichen Pakete sind bereits installiert. Falls notwendig:

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Verwendung

### 1. Desktop-App starten

```powershell
# Aktiviere Virtual Environment (falls noch nicht aktiv)
.venv\Scripts\Activate.ps1

# Starte die Desktop-App
python app.py
```

### 2. Control Panel

Nach dem Start öffnet sich automatisch:

1. **Tkinter Control Panel** - Zeigt Server-Status und Port
2. **Browser mit Web-GUI** - Öffnet sich automatisch nach 1 Sekunde

**Control Panel Features:**
- ✅ Server-Status-Anzeige
- 🌐 "Browser öffnen" - Falls Browser geschlossen wurde
- ❌ "App beenden" - Beendet Server und schließt alle Fenster

### 3. Playlist herunterladen

1. **FFmpeg-Check**: Beim Start wird FFmpeg automatisch gesucht und bei Bedarf heruntergeladen
2. **Playlist-URL eingeben**: YouTube-Playlist-Link in das Eingabefeld
3. **Playlist laden**: Klicke auf "Playlist laden" - du siehst Name und Anzahl der Songs
4. **Download starten**: Klicke auf "Download starten"
5. **Fortschritt beobachten**: Alle Prozesse werden live visualisiert
   - Gesamtfortschritt mit Prozentanzeige
   - Aktueller Song mit Animation
   - Status-Liste aller Songs
6. **Fertig!**: Nach Abschluss wird der Speicherort angezeigt

### 4. App beenden

- Schließe das **Control Panel** Fenster
- Oder klicke auf **"App beenden"** im Control Panel
- Browser kann geschlossen werden, Server läuft weiter

## Dateistruktur

```
Spotify Downloader/
├── app.py                          # Flask Backend + Tkinter GUI
├── templates/
│   └── index.html                  # HTML Template
├── static/
│   ├── style.css                   # CSS Styling
│   ├── script.js                   # JavaScript mit SocketIO
│   └── favicon.svg                 # App Icon
├── ffmpeg/                         # Portable FFmpeg (auto-download)
│   └── bin/
│       ├── ffmpeg.exe
│       └── ffprobe.exe
├── Songs/
│   └── [Playlist Name]/            # Heruntergeladene Songs
├── spotify-playlist-loader-v2.py   # Alte CLI-Version
└── requirements.txt                # Python Dependencies
```

## Features der GUI

### Design
- **Moderne UI**: Dunkles Design mit Spotify-Farbschema
- **Animationen**: Smooth Transitions und Loading-Animationen
- **Icons**: SVG-Icons für alle Aktionen
- **Responsive**: Funktioniert auf Desktop und Mobile

### Fortschrittsvisualisierung
- **Gesamtfortschritt**: Animierter Fortschrittsbalken mit Shimmer-Effekt
- **Prozentanzeige**: Live-Prozentwert
- **Song-Counter**: "X von Y Songs"
- **Aktueller Song**: Großer Bereich mit rotierendem Icon
- **Song-Liste**: Scrollbare Liste mit Status für jeden Song
  - 🔍 Suchen (gelb, rotierend)
  - ⬇️ Download läuft (grün, rotierend)
  - ✅ Erfolgreich (grün)
  - ⏭️ Übersprungen (orange)
  - ❌ Fehler (rot)

### Status-Nachrichten
- **Toast-Notifications**: Automatische Benachrichtigungen in der Ecke
- **Farbcodierung**: Erfolg (grün), Fehler (rot), Info (blau)
- **Auto-Dismiss**: Verschwinden nach 3 Sekunden

## Technische Details

### Desktop-App (Tkinter)
- **Control Panel**: Tkinter-Fenster mit modernem Dark Theme
- **Automatischer Browser-Start**: webbrowser.open() nach 1 Sekunde
- **Port-Management**: Automatische Suche nach freiem Port
- **Thread-basiert**: Flask-Server läuft in separatem Thread

### Backend (Flask)
- **Route `/`**: Hauptseite
- **Route `/check_ffmpeg`**: FFmpeg-Verfügbarkeit prüfen
- **Route `/load_playlist`**: Playlist-Informationen laden
- **Route `/start_download`**: Download-Prozess starten
- **SocketIO Events**:
  - `download_started`: Download beginnt
  - `progress_update`: Fortschritt-Update
  - `song_status`: Status eines einzelnen Songs
  - `download_completed`: Download abgeschlossen
  - `status_update`: Allgemeine Status-Meldungen
  - `error`: Fehlermeldungen

### FFmpeg-Management
- **Automatische Suche**: System-PATH, WinGet-Ordner, typische Pfade
- **Portable Download**: Automatischer Download von gyan.dev
- **PATH-Integration**: Temporäre PATH-Erweiterung für Session
- **Keine Installation nötig**: Läuft aus Projektordner

### Frontend (JavaScript)
- **Socket.IO Client**: Echtzeit-Kommunikation mit Backend
- **Fetch API**: REST-API-Aufrufe
- **DOM Manipulation**: Dynamische UI-Updates
- **Event Handling**: User-Interaktionen

### Styling (CSS)
- **CSS Variables**: Farbschema-Management
- **Flexbox/Grid**: Layout
- **Animations**: Keyframe-Animationen
- **Media Queries**: Responsive Design

## Vergleich CLI vs. Desktop-App

| Feature | CLI (v2.py) | Desktop App (app.py) |
|---------|-------------|----------------------|
| Benutzerfreundlichkeit | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| Fortschrittsanzeige | Text-basiert | Visualisiert |
| Echtzeit-Updates | Keine | Ja (SocketIO) |
| Modernes Design | - | ✅ |
| Desktop-Integration | - | ✅ Tkinter GUI |
| FFmpeg-Installation | Manuell/Prompt | Automatisch |
| Installation | Einfach | Einfach |
| Performance | Schnell | Schnell |
| Mehrbenutzerfähig | Nein | Ja (potenziell) |

## Fehlerbehebung

### FFmpeg-Probleme
Die App lädt FFmpeg automatisch herunter, falls nicht gefunden. Bei Problemen:

**Manuelle Installation:**
```powershell
winget install --id Gyan.FFmpeg -e
```

**Oder:** Lass die App die portable Version herunterladen (geschieht automatisch)

### Port-Konflikte
Die App findet automatisch einen freien Port. Falls dennoch Probleme auftreten:
```powershell
# Prüfe, welche Ports belegt sind
netstat -an | findstr :5000
```

### Browser öffnet nicht
Klicke im Control Panel auf **"🌐 Browser öffnen"** oder öffne manuell die URL, die im Control Panel angezeigt wird.

### Downloads starten nicht
1. Prüfe FFmpeg-Status (Web-GUI oben rechts - sollte grün sein)
2. Schau im Control Panel nach Server-Status
3. Öffne Browser-Konsole (F12) für JavaScript-Fehler
4. Prüfe Terminal für Backend-Logs

### App reagiert nicht
Beende über Control Panel und starte neu:
```powershell
python app.py
```

## Zukünftige Erweiterungen

Mögliche Features für zukünftige Versionen:
- [ ] Spotify-Playlist-Support (wenn API wieder verfügbar)
- [ ] Download-Queue mit Pausieren/Fortsetzen
- [ ] Batch-Download mehrerer Playlists
- [ ] Audio-Quality-Auswahl
- [ ] Dark/Light Theme Toggle
- [ ] Playlist-Import aus Datei
- [ ] Download-Historie
- [ ] Benutzer-Authentifizierung

## Lizenz

Dieses Projekt ist für den persönlichen Gebrauch.

## Kontakt

Bei Fragen oder Problemen, öffne ein Issue auf GitHub.

---

**Made with ❤️ by UST-Germany**
