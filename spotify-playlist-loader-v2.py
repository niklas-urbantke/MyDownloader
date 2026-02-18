# pip install yt-dlp beautifulsoup4 requests

import os
import sys
import requests
from bs4 import BeautifulSoup
import yt_dlp
from urllib.parse import quote
import re
import json
import subprocess
import shutil

# Basis-Ordner für Songs
BASE_SAVE_DIR = "Songs"
os.makedirs(BASE_SAVE_DIR, exist_ok=True)

def download_ffmpeg_portable():
    """Lädt FFmpeg herunter und entpackt es im Projektordner"""
    print("\n🔄 Lade portable FFmpeg herunter...")
    
    ffmpeg_dir = os.path.join(os.getcwd(), "ffmpeg")
    bin_dir = os.path.join(ffmpeg_dir, "bin")
    
    # Prüfe ob schon vorhanden
    if os.path.exists(os.path.join(bin_dir, "ffmpeg.exe")):
        print("✅ Portable FFmpeg bereits vorhanden!")
        return bin_dir
    
    try:
        import zipfile
        import urllib.request
        
        # Download URL für FFmpeg essentials build
        url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
        zip_path = "ffmpeg-temp.zip"
        
        print("   Downloading... (ca. 75 MB, kann etwas dauern)")
        urllib.request.urlretrieve(url, zip_path)
        
        print("   Entpacke...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Extrahiere nur die bin-Dateien
            for member in zip_ref.namelist():
                if '/bin/' in member and member.endswith('.exe'):
                    # Extrahiere direkt nach ffmpeg/bin/
                    filename = os.path.basename(member)
                    target_path = os.path.join(bin_dir, filename)
                    os.makedirs(bin_dir, exist_ok=True)
                    
                    with zip_ref.open(member) as source, open(target_path, 'wb') as target:
                        target.write(source.read())
        
        # Lösche Temp-Datei
        os.remove(zip_path)
        
        print("✅ FFmpeg erfolgreich heruntergeladen!")
        return bin_dir
        
    except Exception as e:
        print(f"❌ Download fehlgeschlagen: {e}")
        return None

def check_ffmpeg():
    """Prüft, ob FFmpeg installiert ist"""
    print("\n" + "="*60)
    print("   System-Anforderungen prüfen")
    print("="*60)
    
    # Prüfe zuerst im Projektordner (portable Version)
    local_ffmpeg = os.path.join(os.getcwd(), "ffmpeg", "bin")
    local_ffmpeg_exe = os.path.join(local_ffmpeg, "ffmpeg.exe")
    
    if os.path.exists(local_ffmpeg_exe):
        print("✅ FFmpeg gefunden (Portable Version im Projektordner)")
        print(f"   Pfad: {local_ffmpeg}")
        # Füge zum PATH hinzu für diese Session
        os.environ["PATH"] = local_ffmpeg + os.pathsep + os.environ.get("PATH", "")
        print("="*60 + "\n")
        return True
    
    # Prüfe ffmpeg im System-PATH
    ffmpeg_path = shutil.which("ffmpeg")
    ffprobe_path = shutil.which("ffprobe")
    
    # Wenn nicht im PATH, prüfe typische Installationsorte
    if not ffmpeg_path:
        possible_paths = [
            r"C:\Program Files\ffmpeg\bin",
            r"C:\ffmpeg\bin",
            r"C:\ProgramData\chocolatey\bin",
        ]
        
        # Prüfe auch WinGet-Installationsordner
        import glob
        winget_pattern = os.path.expanduser(r"~\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg*\ffmpeg-*\bin")
        possible_paths.extend(glob.glob(winget_pattern))
        
        for path_pattern in possible_paths:
            if os.path.exists(path_pattern):
                ffmpeg_test = os.path.join(path_pattern, "ffmpeg.exe")
                if os.path.exists(ffmpeg_test):
                    ffmpeg_path = ffmpeg_test
                    ffprobe_path = os.path.join(path_pattern, "ffprobe.exe")
                    print(f"✅ FFmpeg gefunden: {path_pattern}")
                    os.environ["PATH"] = path_pattern + os.pathsep + os.environ["PATH"]
                    print("="*60 + "\n")
                    return True
    
    if ffmpeg_path and ffprobe_path:
        print("✅ FFmpeg gefunden:")
        print(f"   ffmpeg: {ffmpeg_path}")
        print(f"   ffprobe: {ffprobe_path}")
        print("="*60 + "\n")
        return True
    else:
        print("❌ FFmpeg nicht gefunden!")
        print("\n💡 Lösung: Portable Version herunterladen")
        print("   Die App kann FFmpeg direkt in diesen Ordner herunterladen.")
        print("   Keine Installation oder PATH-Änderung nötig!")
        print("="*60)
        
        choice = input("\n📥 FFmpeg jetzt herunterladen? (j/n): ").strip().lower()
        
        if choice in ['j', 'ja', 'y', 'yes']:
            bin_dir = download_ffmpeg_portable()
            if bin_dir:
                os.environ["PATH"] = bin_dir + os.pathsep + os.environ.get("PATH", "")
                print("\n✅ FFmpeg ist bereit!")
                input("\nDrücke Enter zum Fortfahren...")
                return True
            else:
                print("\n❌ Download fehlgeschlagen.")
                choice2 = input("\nTrotzdem fortfahren (ohne MP3-Konvertierung)? (j/n): ").strip().lower()
                if choice2 in ['j', 'ja', 'y', 'yes']:
                    print("\n⚠️  Videos werden im Original-Format gespeichert (nicht als MP3)")
                    return True
                exit(1)
        else:
            print("\n❌ Ohne FFmpeg kann die App keine MP3s erstellen.")
            exit(1)

def clean(text):
    """Entfernt problematische Zeichen für Dateinamen"""
    return re.sub(r'[^\w\s\-\[\]]', '', text).strip()

def get_playlist_from_web(playlist_url):
    """Lädt Playlist-Daten direkt von der Spotify Webseite (kein API!)"""
    
    print("   Lade Playlist-Daten von Spotify.com...")
    
    # User-Agent damit Spotify uns für einen echten Browser hält
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
    }
    
    try:
        # Lade die Playlist-Seite
        response = requests.get(playlist_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Suche nach JSON-LD Daten (structured data)
        scripts = soup.find_all('script', {'type': 'application/ld+json'})
        
        playlist_name = "Unknown_Playlist"
        songs = []
        
        for script in scripts:
            try:
                data = json.loads(script.string)
                
                # Playlist Name
                if 'name' in data:
                    playlist_name = clean(data['name'])
                    print(f"   Playlist gefunden: {data['name']}")
                
                # Tracks aus dem structured data
                if 'track' in data and isinstance(data['track'], list):
                    for track in data['track']:
                        if '@type' in track and track['@type'] == 'MusicRecording':
                            # Extrahiere Künstler
                            artists = []
                            if 'byArtist' in track:
                                if isinstance(track['byArtist'], list):
                                    artists = [a.get('name', '') for a in track['byArtist']]
                                elif isinstance(track['byArtist'], dict):
                                    artists = [track['byArtist'].get('name', '')]
                            
                            artist_str = ", ".join(artists) if artists else "Unknown Artist"
                            title = track.get('name', 'Unknown Title')
                            
                            songs.append({
                                'title': title,
                                'artist': artist_str,
                                'album': 'Unknown',
                                'duration_ms': 0
                            })
                
            except json.JSONDecodeError:
                continue
        
        if songs:
            print(f"   ✅ {len(songs)} Songs gefunden!")
            return playlist_name, songs
        else:
            print("   ⚠️  Keine Songs in den strukturierten Daten gefunden.")
            print("   Versuche alternative Methode...")
            
            # Fallback: Suche nach Meta-Tags
            title_tag = soup.find('meta', {'property': 'og:title'})
            if title_tag:
                playlist_name = clean(title_tag.get('content', 'Unknown_Playlist'))
            
            # Hinweis: Die Spotify Webseite lädt Songs dynamisch mit JavaScript
            # Deshalb ist Web Scraping hier limitiert
            print("\n   ❌ Die Spotify-Webseite lädt Songs dynamisch mit JavaScript.")
            print("   Web Scraping funktioniert hier nicht zuverlässig.")
            print("\n   💡 Alternative: Exportiere deine Playlist manuell!")
            return None, None
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Fehler beim Laden der Webseite: {e}")
        return None, None

def file_exists(save_dir, artist, title):
    """Prüft, ob ein Song bereits heruntergeladen wurde"""
    pattern = f"{clean(artist)} - {clean(title)}"
    if not os.path.exists(save_dir):
        return False
    for filename in os.listdir(save_dir):
        if filename.startswith(pattern) and filename.endswith(".mp3"):
            return True
    return False

def search_and_download(song, save_dir):
    artist = clean(song["artist"])
    title = clean(song["title"])
    original_url = song.get("original_url", None)  # URL aus der Original-Playlist
    original_title = song.get("original_title", "")
    
    # Prüfe, ob der Song bereits existiert
    if file_exists(save_dir, artist, title):
        print(f"\n→ Überspringe: {artist} - {title} (bereits vorhanden)")
        return "skipped"
    
    # Dateiname im Format: "Künstler - Titel.mp3"
    output_filename = f"{artist} - {title}.%(ext)s"
    output_path = os.path.join(save_dir, output_filename)
    
    # yt-dlp Optionen mit dynamischem Speicherort
    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "0",
        }],
        "outtmpl": output_path,
        "quiet": True,
        "no_warnings": True,
        "continuedl": True,
        "retries": 10,
    }
    
    # Wenn der Parse fehlgeschlagen ist (Unknown Artist), nutze direkt das Original-Video
    if artist == "Unknown Artist" and original_url:
        print(f"\n→ Konnte Titel nicht parsen, nutze Original-Video aus Playlist")
        print(f"   🎵 {original_title}")
        # Für unparsed videos, nutze den Original-Titel
        clean_original = clean(original_title)
        ydl_opts["outtmpl"] = os.path.join(save_dir, f"{clean_original}.%(ext)s")
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([original_url])
            return True
        except Exception as e:
            print(f"   ❌ Download fehlgeschlagen: {e}")
            return False
    
    # Such-Strategien mit starker Präferenz für Topic/Official-Kanäle
    search_variants = [
        # Strategie 1: Explizit nach Topic-Kanälen suchen (Album-Versionen)
        f'"{artist}" "{title}" Topic',
        f'"{title}" "{artist}" "Official Audio" Topic',
        
        # Strategie 2: "Provided to YouTube" Uploads (oft Original-Alben)
        f'"{artist}" "{title}" "Provided to YouTube"',
        
        # Strategie 3: Official Audio/Video
        f'"{title}" "{artist}" "Official Audio"',
        f'"{artist}" "{title}" official',
    ]
    
    print(f"\n→ Suche: {artist} - {title}")
    
    # Suche zuerst nach allen Varianten und wähle die beste aus
    best_match = None
    best_score = 0
    
    for i, query in enumerate(search_variants):
        try:
            search_str = f"ytsearch5:{quote(query)}"  # Nur 5 Ergebnisse pro Suchanfrage
            with yt_dlp.YoutubeDL({**ydl_opts, "quiet": True}) as ydl:
                info = ydl.extract_info(search_str, download=False)
                if not info.get("entries"):
                    continue
                
                # Bewerte die ersten Ergebnisse
                for entry in info["entries"][:3]:  # Top 3 pro Suchanfrage
                    if not entry:
                        continue
                        
                    video_title = entry.get("title", "").lower()
                    channel = entry.get("uploader", "").lower()
                    
                    score = 1  # Minimaler Score
                    
                    # Sehr hohe Priorität: Topic-Kanäle
                    if "topic" in channel or "- topic" in video_title:
                        score += 100
                    
                    # Hohe Priorität: "Provided to YouTube"
                    if "provided to youtube" in video_title:
                        score += 90
                    
                    # Mittlere Priorität: Official Audio/Video
                    if "official audio" in video_title:
                        score += 50
                    elif "official video" in video_title:
                        score += 40
                    elif "official" in video_title:
                        score += 30
                    
                    # Bonus: Kürzere Strategie-Nummer = höhere Priorität
                    score += (10 - i)
                    
                    # Speichere bestes Ergebnis
                    if score > best_score:
                        best_score = score
                        best_match = entry
                        
        except Exception as e:
            continue
    
    # Wenn keine gute Version gefunden wurde UND wir ein Original-Video haben, nutze das
    if (not best_match or best_score < 30) and original_url:
        print("   ⚠️  Keine bessere Version gefunden, nutze Original-Video aus Playlist")
        print(f"   🎵 {original_title}")
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([original_url])
            return True
        except Exception as e:
            print(f"   ❌ Download fehlgeschlagen: {e}")
            return False
    
    # Lade das beste gefundene Video herunter
    if best_match:
        video_title = best_match.get("title", title)
        channel = best_match.get("uploader", "Unknown")
        video_url = best_match.get("webpage_url", best_match.get("url"))
        
        # Info über gefundene Version
        if "topic" in channel.lower() or "- topic" in video_title.lower():
            print("   ✅ TOPIC-Kanal gefunden → Album-Version!")
        elif "provided to youtube" in video_title.lower():
            print("   ✅ 'Provided to YouTube' → Original-Upload!")
        elif "official audio" in video_title.lower():
            print("   ✓ Official Audio gefunden")
        else:
            print("   ℹ️  Standard-Version")
        
        print(f"   → Download von: {video_title}")
        print(f"   → Kanal: {channel}")
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
            return True
        except Exception as e:
            print(f"   ❌ Download fehlgeschlagen: {e}")
            return False
    
    # Als letzter Ausweg: Original-Video
    if original_url:
        print("   ⚠️  Kein Treffer gefunden, nutze Original-Video")
        print(f"   🎵 {original_title}")
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([original_url])
            return True
        except Exception as e:
            print(f"   ❌ Download fehlgeschlagen: {e}")
            return False
    
    print("   → Kein Treffer gefunden und kein Original-Video verfügbar.")
    return False

def parse_video_title(title):
    """Versucht Künstler und Titel aus einem YouTube-Video-Titel zu extrahieren"""
    # Entferne häufige Zusatzinformationen
    original = title
    title = re.sub(r'\(official (video|music video|audio|visualizer|lyric video)\)', '', title, flags=re.IGNORECASE)
    title = re.sub(r'\[official (video|music video|audio|visualizer|lyric video)\]', '', title, flags=re.IGNORECASE)
    title = re.sub(r'\(lyrics?\)', '', title, flags=re.IGNORECASE)
    title = re.sub(r'\[lyrics?\]', '', title, flags=re.IGNORECASE)
    title = re.sub(r'(official|music|hd|4k|video|audio|visualizer|lyric video|lyrics)', '', title, flags=re.IGNORECASE)
    title = re.sub(r'(ft\.?|feat\.?|featuring)[^\-\|]*', '', title, flags=re.IGNORECASE)  # Entferne Features
    title = re.sub(r'\(prod\.?.*?\)', '', title, flags=re.IGNORECASE)  # Entferne Producer
    title = re.sub(r'\s+', ' ', title).strip()  # Mehrfache Leerzeichen entfernen
    
    # Versuche verschiedene Trennzeichen
    for separator in [' - ', ' – ', ' — ', ' | ']:
        if separator in title:
            parts = title.split(separator, 1)
            artist = parts[0].strip()
            song_title = parts[1].strip()
            
            # Validierung: Ist das sinnvoll?
            if len(artist) > 0 and len(song_title) > 0 and len(artist) < 100:
                return artist, song_title
    
    # Wenn kein Trennzeichen gefunden, verwende den original Titel
    return "Unknown Artist", original

def get_youtube_playlist(playlist_url):
    """Lädt alle Videos aus einer YouTube-Playlist"""
    print("\n   Lade YouTube-Playlist...")
    
    # Extrahiere Playlist-ID falls vorhanden
    # Unterstützt URLs wie:
    # - https://www.youtube.com/playlist?list=PLxxx
    # - https://www.youtube.com/watch?v=xxx&list=PLxxx
    # - https://music.youtube.com/playlist?list=PLxxx
    
    playlist_id = None
    if 'list=' in playlist_url:
        # Extrahiere die Playlist-ID
        import urllib.parse
        parsed = urllib.parse.urlparse(playlist_url)
        params = urllib.parse.parse_qs(parsed.query)
        if 'list' in params:
            playlist_id = params['list'][0]
            # Erstelle eine saubere Playlist-URL
            playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"
            print(f"   Playlist-ID gefunden: {playlist_id}")
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,  # Nur Metadaten, keine Videos laden
        'yes_playlist': True,   # WICHTIG: Lade die ganze Playlist, nicht nur ein Video
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(playlist_url, download=False)
            
            if 'entries' not in info:
                print("❌ Keine Videos in der Playlist gefunden!")
                print("   Tipp: Stelle sicher, dass die Playlist öffentlich ist.")
                return None, []
            
            playlist_name = clean(info.get('title', 'YouTube_Playlist'))
            print(f"   Playlist: {info.get('title', 'Unknown')}")
            print(f"   Anzahl Videos: {len(info['entries'])}")
            
            songs = []
            for entry in info['entries']:
                if not entry:
                    continue
                    
                video_title = entry.get('title', '')
                video_url = entry.get('url', '')  # Original Video URL
                video_id = entry.get('id', '')
                
                if not video_title:
                    continue
                
                artist, title = parse_video_title(video_title)
                
                songs.append({
                    'artist': artist,
                    'title': title,
                    'album': 'Unknown',
                    'duration_ms': 0,
                    'original_title': video_title,
                    'original_url': f"https://www.youtube.com/watch?v={video_id}" if video_id else video_url,
                    'original_video_id': video_id
                })
            
            print(f"   ✅ {len(songs)} Songs extrahiert!\n")
            return playlist_name, songs
            
    except Exception as e:
        print(f"   ❌ Fehler beim Laden der YouTube-Playlist: {e}")
        return None, []

def load_from_text_file():
    """Lädt Songs aus einer Textdatei (Alternative zu Spotify)"""
    print("\n" + "="*60)
    print("   📄 Songs aus Textdatei laden")
    print("="*60)
    print("\nErstelle eine Datei 'playlist.txt' mit diesem Format:")
    print("   Künstler - Titel")
    print("   Künstler - Titel")
    print("   ...")
    print("\nBeispiel:")
    print("   Ed Sheeran - Shape of You")
    print("   Adele - Hello")
    print("="*60 + "\n")
    
    if not os.path.exists("playlist.txt"):
        print("❌ Datei 'playlist.txt' nicht gefunden!")
        return None, []
    
    songs = []
    with open("playlist.txt", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            
            if " - " in line:
                parts = line.split(" - ", 1)
                artist = parts[0].strip()
                title = parts[1].strip()
                songs.append({
                    "artist": artist,
                    "title": title,
                    "album": "Unknown",
                    "duration_ms": 0
                })
    
    print(f"✅ {len(songs)} Songs aus Textdatei geladen!\n")
    return "Meine_Playlist", songs

# ─── Hauptprogramm ───────────────────────────────────────
if __name__ == "__main__":
    # Prüfe zuerst, ob FFmpeg installiert ist
    check_ffmpeg()
    
    print("=" * 60)
    print("   Playlist Downloader v2")
    print("   YouTube + Spotify (ohne API)")
    print("=" * 60)
    
    print("\nWähle eine Quelle:")
    print("  [1] Spotify Playlist-URL (experimentell, Web Scraping)")
    print("  [2] Songs aus Textdatei laden")
    print("  [3] YouTube Playlist-URL (⭐ EMPFOHLEN)")
    
    choice = input("\nDeine Wahl (1/2/3): ").strip()
    
    if choice == "2":
        playlist_name, songs = load_from_text_file()
        if not songs:
            print("\n❌ Keine Songs geladen. Beende...")
            exit(1)
    elif choice == "3":
        print("\n" + "="*60)
        print("   YouTube Playlist Downloader")
        print("="*60)
        print("\nDie App wird:")
        print("  1. Alle Video-Titel aus der Playlist extrahieren")
        print("  2. Nach Künstler und Titel parsen")
        print("  3. Nach besseren Versionen auf Topic/Official-Kanälen suchen")
        print("  4. Die Album-Versionen bevorzugt herunterladen")
        print("="*60 + "\n")
        
        playlist_url = input("YouTube Playlist-URL einfügen: ").strip()
        
        if "youtube.com" not in playlist_url and "youtu.be" not in playlist_url:
            print("❌ Das sieht nicht nach einer YouTube-URL aus.")
            exit(1)
        
        playlist_name, songs = get_youtube_playlist(playlist_url)
        
        if not songs:
            print("\n❌ Keine Songs geladen. Beende...")
            exit(1)
    else:
        playlist_url = input("\nSpotify Playlist Link einfügen: ").strip()
        
        if "spotify.com/playlist/" not in playlist_url:
            print("Das sieht nicht nach einem gültigen Spotify-Playlist-Link aus.")
            exit(1)
        
        playlist_name, songs = get_playlist_from_web(playlist_url)
        
        if not songs:
            print("\n💡 Tipp: Nutze Option [3] mit einer YouTube-Playlist!")
            print("   oder Option [2] mit einer Textdatei")
            exit(1)
    
    # Erstelle Playlist-Ordner
    save_dir = os.path.join(BASE_SAVE_DIR, playlist_name)
    os.makedirs(save_dir, exist_ok=True)
    
    print(f"\nPlaylist: {playlist_name}")
    print(f"Songs gefunden: {len(songs)}")
    print(f"Speicherort: {os.path.abspath(save_dir)}")
    print("\n" + "=" * 60)
    
    success_count = 0
    skipped_count = 0
    
    for i, song in enumerate(songs, 1):
        # Nach jeweils 100 Songs nachfragen
        if i > 1 and (i - 1) % 100 == 0:
            print("\n" + "=" * 60)
            print(f"Fortschritt: {i-1}/{len(songs)} Songs verarbeitet")
            print(f"Erfolgreich: {success_count} | Übersprungen: {skipped_count}")
            fortsetzung = input("\nMöchtest du fortfahren? (j/n): ").strip().lower()
            if fortsetzung != "j" and fortsetzung != "ja":
                print("\nAbbruch durch Benutzer.")
                break
            print("=" * 60)
        
        print(f"\n[{i}/{len(songs)}]")
        result = search_and_download(song, save_dir)
        
        if result == "skipped":
            skipped_count += 1
        elif result:
            success_count += 1
    
    print("\n" + "=" * 60)
    print("   Download abgeschlossen!")
    print("=" * 60)
    print(f"Erfolgreich heruntergeladen: {success_count}")
    print(f"Übersprungen (bereits vorhanden): {skipped_count}")
    print(f"Fehlgeschlagen: {len(songs) - success_count - skipped_count}")
    print(f"\nSpeicherort: {os.path.abspath(save_dir)}")
