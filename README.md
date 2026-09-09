# MyDownloader

> Moderner Musik- & Video-Downloader — Electron + Vue 3, mit gebündeltem
> yt-dlp und FFmpeg. Keine Abhängigkeiten, einfach installieren und loslegen.

MyDownloader 5 baut auf dem kompletten Neuaufbau von v4 (Electron + Vue 3,
Batix-Design-System) auf und bringt einen großen Schwung neuer Funktionen:
Abos, Spotify-Import, Metadaten-Editor, Auto-Updates, System-Tray u. v. m.

## Features

### Downloads
- **Downloads**: einzelne Videos/Songs, komplette Playlists (eigene
  Unterordner), **ganze Kanäle** (Videos/Shorts/Livestreams wählbar) und
  Shorts — Warteschlange mit bis zu 5 parallelen Downloads
- **Pausieren & Fortsetzen** einzelner Downloads; die Warteschlange übersteht
  App-Neustarts (unterbrochene Downloads werden fortgesetzt)
- **Zeitplaner**: Downloads zu einem Zeitpunkt planen oder die Queue auf ein
  tägliches Zeitfenster begrenzen (z. B. nachts)
- **Playlist-Abos**: abonnierte Playlists/Kanäle werden automatisch geprüft,
  nur neue Videos werden geladen
- **Mehrere Qualitätsstufen gleichzeitig** (z. B. 1080p + 480p) — pro Download
  oder in Vorlagen
- **Kapitel-Splitting** (lange Videos anhand der Kapitel in Einzeldateien)
  und **Ausschnitt-Download** (nur einen Zeitbereich laden)
- **Vorlagen**: Download-Presets mit Format, Qualität und eigenen
  Speicherorten — auf Wunsch Video **und** Audio in einem Rutsch
- **Untertitel** (.srt) und **SponsorBlock**-Integration

### Audio & Metadaten
- **Audio**: MP3, M4A, OPUS, FLAC, WAV — Cover & Metadaten automatisch
- **Video**: MP4, MKV, WEBM — Auflösung begrenzbar (480p bis 4K)
- **Metadaten-Editor** mit MusicBrainz-Vorschlägen und Cover-Tausch
- **Lautstärke-Normalisierung** (ReplayGain-Tags oder EBU-R128-loudnorm)
- **Songtexte** automatisch einbetten (LRCLIB, synchronisierte .lrc-Dateien)
- **Eigenes Datei-Schema** mit Platzhaltern (`{artist}/{album}/{track} - {title}`)

### Integration & Komfort
- **Hörprobe** vor dem Download (30 Sekunden, auch für Playlist-Einträge)
- **Spotify-Import**: Playlists/Alben mit dem eigenen Spotify-Konto laden und
  als Audio-Downloads übernehmen (Client-ID in den Einstellungen, PKCE-Login)
- **YouTube-Konto-Anbindung** über Browserfenster — für 18+-Inhalte (Cookies
  bleiben lokal)
- **System-Tray** mit Hintergrund-Downloads, **Drag & Drop** für Links und
  URL-Listen, **Clipboard-Watcher**, native Benachrichtigungen mit
  Ordner-Sprung, Dock-/Taskbar-Fortschritt
- **Deep-Links**: `mydownloader://download?url=…` aus Browser/Bookmarklet
- **Auto-Updates** über GitHub Releases + Offline-Updates per
  `.urbupdate`-Datei (`node scripts/make-urbupdate.mjs`)
- **Statistik-Dashboard**, durchsuchbarer Verlauf mit Zeitraum-Filtern,
  Onboarding-Assistent, Hell-/Dunkel-Modus, Deutsch & Englisch
- **Import aus v3** (Einstellungen + Download-Verlauf)
- **Alles gebündelt**: yt-dlp, FFmpeg und die nötige JavaScript-Runtime sind
  in der App enthalten — keine Installation von Python, Node oder FFmpeg nötig

## Installation

Alle Installer gibt es auf der
[Releases-Seite](https://github.com/niklas-urbantke/YouTube-Downloader/releases).

| Plattform | Datei | Hinweis |
| --- | --- | --- |
| **Windows** | `MyDownloader-Setup-<version>.exe` | Setup-Assistent (Installationsordner wählbar) |
| **Windows (portable)** | `MyDownloader-<version>-portable.exe` | Keine Installation, direkt starten |
| **macOS** | `MyDownloader-<version>-arm64.dmg` (Apple Silicon) / `…-x64.dmg` (Intel) | Unsigniert: beim ersten Start Rechtsklick → „Öffnen“ |
| **Linux (universal)** | `MyDownloader-<version>-x86_64.AppImage` | Ausführbar machen (`chmod +x`) und starten |
| **Debian/Ubuntu** | `mydownloader_<version>_amd64.deb` | `sudo apt install ./mydownloader_<version>_amd64.deb` |
| **Arch Linux** | `mydownloader-<version>-x64.pacman` | `sudo pacman -U mydownloader-<version>-x64.pacman` |

### Arch Linux über AUR

Das Paket-Rezept liegt unter [`packaging/aur/PKGBUILD`](packaging/aur/PKGBUILD)
(`mydownloader-bin`, repackt das offizielle `.deb`). Lokal bauen:

```bash
cd packaging/aur
updpkgsums && makepkg -si
```

Zum Veröffentlichen im AUR: PKGBUILD in ein AUR-Git-Repo
(`ssh://aur@aur.archlinux.org/mydownloader-bin.git`) pushen.

## Entwicklung

Voraussetzungen: Node.js ≥ 20, npm.

```bash
npm install                  # Abhängigkeiten
node scripts/fetch-binaries.mjs   # yt-dlp + FFmpeg für die eigene Plattform
npm run dev                  # App im Dev-Modus (Hot Reload)
```

Weitere Befehle:

```bash
npm run typecheck            # TypeScript-Prüfung (main + renderer)
npm run build                # Bundles bauen (out/)
npm run build:mac            # macOS-Installer (release/)
npm run build:win            # Windows-Installer
npm run build:linux          # Linux-Pakete
```

### Projektstruktur

```
src/main/        Electron-Main-Process: Download-Engine (yt-dlp), Queue,
                 Settings/History-Stores, Binary-Resolver, IPC
src/preload/     Typisierte IPC-Bridge (window.api)
src/renderer/    Vue-3-App: Views, Pinia-Stores, Design-System-Komponenten
src/shared/      Gemeinsame Typen & IPC-Kanäle (einzige Vertragsquelle)
scripts/         fetch-binaries.mjs (yt-dlp/FFmpeg-Download je Plattform)
packaging/aur/   PKGBUILD für Arch Linux
.github/         CI (Typecheck/Build) + Release-Pipeline
```

### Wie die App self-contained bleibt

- **yt-dlp** und **FFmpeg** werden beim Build als statische Binaries unter
  `resources/bin/<platform>-<arch>/` mitgeliefert (`extraResources`).
- yt-dlp braucht für YouTube eine JavaScript-Runtime (Node ≥ 22): dafür wird
  die eigene Electron-Executable im `ELECTRON_RUN_AS_NODE`-Modus als Runtime
  übergeben — kein zusätzlicher Download nötig.

### yt-dlp aktuell halten (wichtig für Releases)

YouTube sperrt in unregelmäßigen Abständen die Zugriffswege, die ältere
yt-dlp-Stände benutzen. Ein Release mit veraltetem yt-dlp fällt deshalb nicht
sofort auf, sondern erst Wochen später beim Nutzer: der Download startet und
bricht mitten im Vorgang mit `HTTP Error 403` ab. Dagegen greifen drei Dinge:

1. **Der Build zieht immer den neuesten Stand.** `scripts/fetch-binaries.mjs`
   vergleicht das vorhandene Binary mit der neuesten Veröffentlichung, statt nur
   auf Vorhandensein zu prüfen, und notiert den geladenen Stand in
   `resources/bin/<ziel>/yt-dlp.version`. `npm run build:mac|win|linux` und
   `npm run release` rufen das automatisch auf, ein altes lokales Binary kann
   also nicht mehr versehentlich ins Release wandern. Die tatsächlich gebündelte
   Version steht im Build-Log (`Bundled yt-dlp version: …`).

   ```bash
   node scripts/fetch-binaries.mjs                          # neuesten Stand holen
   node scripts/fetch-binaries.mjs --ytdlp-version 2026.08.19  # Version festnageln
   node scripts/fetch-binaries.mjs --offline                # ohne Netz bauen
   ```

2. **Die App aktualisiert sich selbst.** Beim Start prüft sie den Stand gegen
   die neueste Veröffentlichung (Einstellung „yt-dlp aktuell halten“:
   automatisch / nur melden / aus).

3. **Das Update landet in einem beschreibbaren Ordner.** Aktualisiert wird eine
   Kopie unter `userData/bin/`, die anschließend dem ausgelieferten Binary
   vorgezogen wird. Der Programmordner selbst ist auf den meisten Installationen
   schreibgeschützt (Linux-AppImage ist ein read-only Mount, Windows-Setups nach
   `Program Files` gehören dem Administrator), dort scheiterte das frühere
   In-Place-Update mit `Unable to write to …`. Bringt eine neue App-Version ein
   neueres Binary mit, wird die veraltete Kopie beim Start automatisch verworfen.

## Lizenz

[MIT](LICENSE) · gebündelte Komponenten: yt-dlp (Unlicense), FFmpeg (GPL/LGPL),
Electron (MIT), Vue (MIT). Bitte nur Inhalte herunterladen, für die du die
nötigen Rechte hast.
