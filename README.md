# MyDownloader

> Moderner Musik- & Video-Downloader — Electron + Vue 3, mit gebündeltem
> yt-dlp und FFmpeg. Keine Abhängigkeiten, einfach installieren und loslegen.

MyDownloader 4 ist der komplette Neuaufbau der bisherigen Python/tkinter-App
(v3): neue Architektur, neues UI im Batix-Design-System, gleiche und viele
neue Funktionen.

## Features

- **Downloads**: einzelne Videos/Songs, komplette Playlists (eigene
  Unterordner), Warteschlange mit bis zu 5 parallelen Downloads
- **Audio**: MP3, M4A, OPUS, FLAC, WAV — Qualität wählbar, Cover-Thumbnail
  und Metadaten werden automatisch eingebettet
- **Video**: MP4, MKV, WEBM — Auflösung begrenzbar (480p bis 4K)
- **Vorschau** vor dem Download (Titel, Kanal, Dauer, Playlist-Inhalt)
- **Verlauf** mit Suche, Filtern, Re-Download und „Im Ordner zeigen“
- **Untertitel** (.srt) in beliebigen Sprachen
- **SponsorBlock**-Integration (Sponsor-Segmente automatisch entfernen)
- **Clipboard-Watcher** (opt-in): erkennt kopierte Video-URLs
- **Selbst-aktualisierendes yt-dlp** (Einstellungen → Komponenten)
- **Import aus v3** (Einstellungen + Download-Verlauf)
- Geschwindigkeits-Limit, native Benachrichtigungen, Dock-/Taskbar-Fortschritt
- Hell-/Dunkel-Modus, Deutsch & Englisch
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

## Release erstellen

```bash
# Version in package.json anheben, dann:
git tag v4.0.0
git push origin v4.0.0
```

Die GitHub-Actions-Pipeline (`.github/workflows/release.yml`) baut daraufhin
auf Windows-, macOS- und Linux-Runnern alle Installer und veröffentlicht sie
als GitHub-Release.

## Alte Versionen

- **v3 (Python/tkinter)**: über den Tag [`v3.0.0`](https://github.com/niklas-urbantke/YouTube-Downloader/tree/v3.0.0)
- **Komplettes Archiv** (Flask-UI, C++-Prototyp, Spotify-Loader …): auf dem
  [`recovery`-Branch](https://github.com/niklas-urbantke/YouTube-Downloader/tree/recovery)

## Lizenz

[MIT](LICENSE) · gebündelte Komponenten: yt-dlp (Unlicense), FFmpeg (GPL/LGPL),
Electron (MIT), Vue (MIT). Bitte nur Inhalte herunterladen, für die du die
nötigen Rechte hast.
