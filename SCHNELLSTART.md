# 🚀 Schnellstart Guide

## App starten

1. **Öffne PowerShell** im Projektordner
2. **Aktiviere Virtual Environment:**
   ```powershell
   .venv\Scripts\Activate.ps1
   ```
3. **Starte die App:**
   ```powershell
   python app.py
   ```

## Was passiert?

### 1️⃣ Control Panel öffnet sich
Ein kleines Tkinter-Fenster wird angezeigt mit:
- ✅ Server-Status (läuft)
- 🌐 URL und Port-Nummer
- Buttons: "Browser öffnen" und "App beenden"

### 2️⃣ Browser öffnet automatisch
Nach 1 Sekunde öffnet sich dein Standard-Browser mit der Web-GUI.

### 3️⃣ FFmpeg wird geprüft
Beim ersten Start:
- App sucht nach FFmpeg auf deinem System
- Falls nicht gefunden: **Automatischer Download** (~75 MB)
- Installation erfolgt im Projektordner (`ffmpeg/bin/`)
- Keine Admin-Rechte nötig!

## Playlist herunterladen

1. **Playlist-URL eingeben**
   - Kopiere YouTube-Playlist-Link
   - Füge ihn ins Eingabefeld ein
   - Beispiel: `https://www.youtube.com/playlist?list=...`

2. **Playlist laden**
   - Klick auf "Playlist laden"
   - Warte kurz (lädt Playlist-Infos)
   - Grüne Box erscheint mit Name und Song-Anzahl

3. **Download starten**
   - Klick auf "Download starten"
   - Progress-Bereich erscheint
   - Live-Updates für jeden Song!

## Live-Visualisierung

Während des Downloads siehst du:

### 📊 Gesamtfortschritt
- Großer animierter Balken mit Shimmer-Effekt
- Prozentanzeige (z.B. 45%)
- "X von Y Songs" Counter

### 🎵 Aktueller Song
- Rotierendes Icon
- Name des gerade heruntergeladenen Songs

### 📝 Song-Liste
Jeder Song zeigt Status:
- 🔍 **Suchen** (gelb, animiert) - Sucht nach Album-Version
- ⬇️ **Download läuft** (grün, animiert) - Lädt herunter
- ✅ **Erfolgreich** (grün) - Fertig!
- ⏭️ **Übersprungen** (orange) - Bereits vorhanden
- ❌ **Fehler** (rot) - Problem aufgetreten

## Nach dem Download

### ✅ Erfolgsmeldung
- Grünes Häkchen-Icon
- "X Songs erfolgreich heruntergeladen"
- Speicherort wird angezeigt

### 📁 Dateien finden
Deine MP3s sind hier:
```
Projektordner/Songs/[Playlist Name]/Künstler - Titel.mp3
```

Beispiel:
```
Songs/
└── Mixtape 25/
    ├── Drake - God's Plan.mp3
    ├── Post Malone - Circles.mp3
    └── ...
```

## App beenden

**Option 1:** Schließe das Control Panel Fenster

**Option 2:** Klick im Control Panel auf "❌ App beenden"

Der Browser kann jederzeit geschlossen werden - Server läuft weiter!

## Tipps & Tricks

### 🔄 Browser erneut öffnen
Versehentlich Browser geschlossen?
- Klick auf "🌐 Browser öffnen" im Control Panel
- Oder öffne die URL manuell (steht im Control Panel)

### 🎯 Mehrere Playlists
Nach Abschluss:
- Klick auf "Neuen Download starten"
- Neue Playlist-URL eingeben
- Erneut herunterladen!

### ⚡ Performance
- Größere Playlists (100+ Songs) dauern länger
- Download-Geschwindigkeit hängt von deiner Internetverbindung ab
- Album-Suche kann 5-10 Sekunden pro Song dauern

### 💾 Speicherplatz
- MP3s sind ca. 3-5 MB pro Song
- 100 Songs ≈ 300-500 MB
- FFmpeg portable ≈ 75 MB (einmalig)

## Häufige Fragen

**Q: Muss ich FFmpeg selbst installieren?**
A: Nein! Die App lädt es automatisch herunter, falls nicht vorhanden.

**Q: Werden Songs doppelt heruntergeladen?**
A: Nein! Die App erkennt bereits vorhandene Dateien und überspringt sie.

**Q: Woher kommen die Songs?**
A: Von YouTube. Die App sucht nach "Album"-Versionen (Topic Channels) für beste Qualität.

**Q: Kann ich die Playlist im Browser lassen?**
A: Ja! Schließe einfach den Browser. Die URL steht im Control Panel, falls du sie wieder brauchst.

**Q: Funktioniert es mit privaten Playlists?**
A: Nur mit öffentlichen YouTube-Playlists. Private funktionieren nicht.

**Q: Kann ich mehrere Downloads gleichzeitig?**
A: Momentan nur einen Download gleichzeitig. Nach Abschluss kannst du den nächsten starten.

## Probleme?

### FFmpeg lädt nicht herunter
Manuell installieren:
```powershell
winget install --id Gyan.FFmpeg -e
```

### "Port bereits belegt"
Die App findet automatisch einen freien Port. Im unwahrscheinlichen Fall von Problemen:
- Schließe andere Programme, die Server starten könnten
- Starte die App neu

### Songs werden nicht gefunden
- Prüfe, ob die Playlist-URL korrekt ist
- Stelle sicher, dass die Playlist öffentlich ist
- Internet-Verbindung prüfen

### Browser bleibt leer
- Warte 2-3 Sekunden nach dem Start
- Klick auf "Browser öffnen" im Control Panel
- Oder gib die URL manuell ein

---

**Viel Spaß beim Musik-Download! 🎵**
