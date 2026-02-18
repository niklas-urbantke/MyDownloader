# 🚀 SCHNELLSTART - Ultimate Music & Video Downloader v3.0

## ⚡ In 3 Schritten starten:

### 1️⃣ Installation (einmalig)
```bash
pip install -r requirements_v3.txt
```

### 2️⃣ Starten
```bash
python app_tkinter_v3.py
```

### 3️⃣ Downloaden!
- URL eingeben → "Einzeln Download" ODER
- URL eingeben → "Playlist laden" → "Playlist Download starten"

---

## 🎯 Die 5 häufigsten Anwendungen:

### 1. 🎵 Einzelnen Song downloaden
```
1. YouTube-Video-URL kopieren
2. In App einfügen
3. "Einzeln Download" klicken
4. Fertig! (Datei liegt in Songs-Ordner)
```

### 2. 📋 Ganze Playlist downloaden
```
1. YouTube-Playlist-URL kopieren
2. In App einfügen
3. "Playlist laden" klicken
4. Warten (Info wird angezeigt)
5. "Playlist Download starten" klicken
6. Kaffee holen ☕
```

### 3. 📑 Viele einzelne Videos (Queue)
```
1. Bei jedem Video: URL eingeben → "Zur Queue"
2. Zu Tab "Queue" wechseln
3. "Queue starten" klicken
4. Alle werden nacheinander geladen
```

### 4. 📄 Bulk-Import aus Datei
```
1. Textdatei erstellen mit URLs (eine pro Zeile):
   https://youtube.com/watch?v=...
   https://youtube.com/watch?v=...
   https://youtube.com/watch?v=...

2. Tab "Queue" öffnen
3. "Aus Datei importieren" klicken
4. Datei auswählen
5. "Queue starten" klicken
```

### 5. 👁️ Vor Download prüfen
```
1. URL eingeben
2. "Vorschau" klicken
3. Titel, Uploader, Dauer prüfen
4. Wenn OK → "Einzeln Download"
```

---

## ⚙️ Wichtige Einstellungen:

### Download-Ordner ändern:
```
📁 Im Download-Tab:
"🗂️ Ändern" klicken → Ordner wählen → Fertig!
(Wird automatisch gespeichert)
```

### Audio-Format ändern:
```
Tab "Einstellungen" → Audio-Format: MP3/M4A/FLAC/... auswählen
→ "Einstellungen speichern"
```

### Geschwindigkeit begrenzen:
```
Tab "Einstellungen" → Geschwindigkeitslimit: z.B. "5" (für 5 MB/s)
→ "Einstellungen speichern"
```

### Untertitel aktivieren:
```
Tab "Einstellungen" → "Untertitel herunterladen" aktivieren
→ Sprachen: "de,en" → "Einstellungen speichern"
```

---

## 🔥 Pro-Tipps:

### Tipp 1: Beste Qualität
```
Einstellungen:
- Format: FLAC
- Qualität: 0 (Beste)
- Thumbnail einbetten: ✓
- Metadaten einbetten: ✓
```

### Tipp 2: Kleinste Dateien
```
Einstellungen:
- Format: OPUS oder M4A
- Qualität: 7
```

### Tipp 3: Standard (empfohlen)
```
Einstellungen:
- Format: MP3
- Qualität: 0 oder 2
- Thumbnail: ✓
- Metadaten: ✓
```

### Tipp 4: Mehrere Downloads parallel
```
Nutze Queue-System:
- Alle URLs zur Queue hinzufügen
- Einmal "Queue starten"
- App arbeitet alle ab
```

### Tipp 5: URL aus Clipboard
```
Tab "Queue":
1. URLs kopieren (z.B. mehrere auf einmal)
2. "Aus Zwischenablage" klicken
3. Alle werden importiert!
```

---

## ❌ Häufige Probleme (und Lösung):

### "FFmpeg nicht gefunden"
```
→ Einfach warten! App lädt es automatisch herunter.
→ Dauert beim ersten Mal ~2 Minuten.
```

### "Download schlägt fehl"
```
→ In Einstellungen: "yt-dlp aktualisieren" klicken
→ YouTube ändert häufig was, yt-dlp muss aktuell sein
```

### "Langsam!"
```
→ Einstellungen: Geschwindigkeitslimit entfernen (leer lassen)
→ Oder: Format auf MP3 statt FLAC
```

### "Kein Thumbnail sichtbar"
```
→ Einstellungen: "Thumbnail einbetten" aktivieren
→ App neu starten
```

### "App startet nicht"
```
→ Prüfen: python app_tkinter_v3.py
→ Fehlermeldung lesen
→ Meist: pip install -r requirements_v3.txt
```

---

## 📱 Shortcuts & Tricks:

- **Tab wechseln**: Strg + Tab
- **URL einfügen**: Strg + V im Eingabefeld
- **App schließen**: Alt + F4 oder X-Button
- **History durchsuchen**: Tab "History" → Scrollen
- **Queue-Eintrag löschen**: Rechtsklick → Entfernen

---

## 🎨 Interface-Übersicht:

```
┌─────────────────────────────────────────┐
│  📥 Download  📑 Queue  📜 History      │  ← Tabs
│  ⚙️ Einstellungen  ℹ️ Info              │
├─────────────────────────────────────────┤
│  🔗 URL: [_________________] [👁️]      │  ← URL + Vorschau
│  [📋 Playlist laden] [⬇️ Einzeln]       │  ← Buttons
│  [➕ Zur Queue]                          │
├─────────────────────────────────────────┤
│  ℹ️ Informationen:                      │  ← Video-Info
│  Titel, Uploader, etc.                  │
├─────────────────────────────────────────┤
│  📁 Download-Ordner: [____] [🗂️ Ändern] │  ← Ordner
│  [▶️ Download starten] [⏹️ Abbrechen]   │  ← Kontrolle
├─────────────────────────────────────────┤
│  📊 Fortschritt: 5/10 Songs             │  ← Progress
│  [████████░░░░░░░░] 50%                │
├─────────────────────────────────────────┤
│  📝 Aktivität:                          │  ← Logs
│  ✅ Song 1 heruntergeladen              │
│  📥 Song 2 wird geladen...              │
└─────────────────────────────────────────┘
```

---

## ✅ Checkliste vor dem ersten Download:

- [ ] Python installiert (3.8+)
- [ ] Requirements installiert (`pip install -r requirements_v3.txt`)
- [ ] App gestartet (`python app_tkinter_v3.py`)
- [ ] FFmpeg-Check OK (in Logs ersichtlich)
- [ ] Download-Ordner gesetzt (Standard: ./Songs)
- [ ] Format gewählt (Standard: MP3)
- [ ] Internet-Verbindung aktiv

---

## 🆘 Support:

1. **README_V3.md lesen** - Ausführliche Dokumentation
2. **Logs prüfen** - Unten in der App (📝 Aktivität)
3. **yt-dlp updaten** - Tab Einstellungen
4. **FFmpeg prüfen** - Sollte automatisch geladen werden

---

## 🎉 Los geht's!

```bash
python app_tkinter_v3.py
```

**Erste URL eingeben und auf "Einzeln Download" klicken!**

🎵 Happy Downloading! 🎵
