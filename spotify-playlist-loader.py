# pip install spotipy yt-dlp python-dotenv
# (optional: pip install mutagen   → für bessere Tags)

import os
import sys
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import yt_dlp
from urllib.parse import quote
import re
import traceback
from dotenv import load_dotenv  # optional, für .env Datei

# ─── Konfiguration ────────────────────────────────────────
load_dotenv()  # lädt .env Datei falls vorhanden

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# Prüfe, ob Credentials vorhanden sind
if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
    print("\n" + "="*60)
    print("   FEHLER: Spotify API-Credentials fehlen!")
    print("="*60)
    print("\nBitte erstelle eine .env Datei mit deinen Spotify API-Zugangsdaten:")
    print("\n1. Gehe zu: https://developer.spotify.com/dashboard")
    print("2. Logge dich ein und erstelle eine neue App")
    print("3. Kopiere Client ID und Client Secret")
    print("4. Erstelle eine Datei '.env' im selben Ordner mit folgendem Inhalt:\n")
    print("   SPOTIFY_CLIENT_ID=deine_client_id")
    print("   SPOTIFY_CLIENT_SECRET=dein_client_secret\n")
    print("="*60)
    input("\nDrücke Enter zum Beenden...")
    exit(1)

# Basis-Ordner für Songs
BASE_SAVE_DIR = "Songs"
os.makedirs(BASE_SAVE_DIR, exist_ok=True)

# ─── Spotify Client mit User Authorization ────────────────────
print("\n" + "="*60)
print("   Spotify User Login")
print("="*60)
print("\nDu musst dich mit deinem Spotify-Account anmelden.")
print("Es öffnet sich ein Browser-Fenster für die Anmeldung.")
print("\nWichtig: Nach der Anmeldung wirst du zu einer URL weitergeleitet.")
print("Die Seite wird nicht laden (das ist normal!).")
print("Kopiere die VOLLSTÄNDIGE URL aus der Adresszeile und füge sie hier ein.")
print("="*60 + "\n")

try:
    # Lösche alten Cache, um neue Berechtigungen anzufordern
    cache_file = ".spotify_cache"
    if os.path.exists(cache_file):
        os.remove(cache_file)
        print("🔄 Cache gelöscht - neue Berechtigungen werden angefordert...\n")
    
    # OAuth mit User-Login für vollen Zugriff
    # Erweiterte Scopes für alle Playlist-Typen
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri="http://127.0.0.1:8888/callback",
        scope="playlist-read-private playlist-read-collaborative user-library-read",
        cache_path=cache_file,
        open_browser=True,
        show_dialog=True  # Zeigt immer den Login-Dialog
    ))
    
    # Teste die Verbindung
    user = sp.current_user()
    print(f"✅ Erfolgreich angemeldet als: {user['display_name']}")
    print(f"   Spotify ID: {user['id']}\n")
    
except Exception as e:
    print("\n" + "="*60)
    print("   ❌ FEHLER: Spotify Login fehlgeschlagen!")
    print("="*60)
    print(f"\nFehlertyp: {type(e).__name__}")
    print(f"Fehlermeldung: {str(e)}")
    print("\n--- Vollständiger Fehler-Traceback ---")
    traceback.print_exc()
    print("\n" + "="*60)
    print("\n🔧 Bitte überprüfe:")
    print("   1. Deine Client ID und Client Secret in der .env Datei")
    print("   2. Gehe zu: https://developer.spotify.com/dashboard")
    print("   3. Stelle sicher, dass 'http://localhost:8888/callback'")
    print("      als Redirect URI in deiner App eingetragen ist")
    print("   4. Öffne die App-Einstellungen und füge die Redirect URI hinzu")
    input("\nDrücke Enter zum Beenden...")
    exit(1)

def clean(text):
    """Entfernt problematische Zeichen für Dateinamen"""
    return re.sub(r'[^\w\s\-\[\]]', '', text).strip()

def get_playlist_info(playlist_url):
    """Holt Playlist-Name und ID"""
    playlist_id = playlist_url.split("/playlist/")[1].split("?")[0]
    
    # Versuche Playlist-Daten zu laden
    try:
        playlist = sp.playlist(playlist_id, fields="name,id,tracks.total,public,owner.display_name")
    except Exception as e:
        print(f"\n⚠️  Fehler beim Abrufen der Playlist-Info: {e}")
        # Debugging: Zeige was zurückkommt
        try:
            playlist = sp.playlist(playlist_id)
            print(f"Debug - Verfügbare Felder: {list(playlist.keys())}")
        except:
            pass
        raise
    
    # Debug-Ausgabe
    print(f"   Playlist-Name: {playlist.get('name', 'Unbekannt')}")
    if 'owner' in playlist and 'display_name' in playlist['owner']:
        print(f"   Besitzer: {playlist['owner']['display_name']}")
    if 'public' in playlist:
        print(f"   Öffentlich: {'Ja' if playlist['public'] else 'Nein'}")
    
    return {
        "name": clean(playlist.get("name", "Unknown_Playlist")),
        "id": playlist_id,
        "total": playlist.get("tracks", {}).get("total", 0) if "tracks" in playlist else 0
    }

def file_exists(save_dir, artist, title):
    """Prüft, ob ein Song bereits heruntergeladen wurde"""
    # Suche nach Dateien mit ähnlichem Namen (ohne Video-ID)
    pattern = f"{clean(artist)} - {clean(title)}"
    for filename in os.listdir(save_dir):
        if filename.startswith(pattern) and filename.endswith(".mp3"):
            return True
    return False

def get_playlist_tracks(playlist_url):
    """Holt alle Tracks aus der Playlist (mit Paginierung für >100 Songs)"""
    tracks = []
    offset = 0
    limit = 100
    
    # Extrahiere Playlist ID
    playlist_id = playlist_url.split("/playlist/")[1].split("?")[0]
    
    print("   Lade Songs")
    
    while True:
        try:
            # Nutze user-spezifischen API-Call mit market parameter
            results = sp.playlist_items(
                playlist_id, 
                limit=limit, 
                offset=offset,
                fields="items(track(name,artists,album,duration_ms)),next"
            )
            items = results.get('items', [])
            
            if not items:
                break
                
            tracks.extend(items)
            print(f"   Progress: {len(tracks)} Songs geladen...", end="\r")
            
            # Wenn es keine weiteren Songs gibt, abbrechen
            if results.get('next') is None:
                break
                
            offset += limit
            
        except Exception as e:
            error_str = str(e)
            print(f"\n   ⚠️  Fehler beim Laden von Songs (Offset {offset}): {error_str}")
            
            # Wenn 403, gebe detaillierte Info
            if "403" in error_str:
                print("\n   ⚠️  403 Forbidden trotz User-Login!")
                print("   Mögliche Ursache: Spotify App im Development Mode")
                print("   Lösung: Wechsle zu 'Extended Quota Mode' im Dashboard")
                print("   → https://developer.spotify.com/dashboard")
                
            break
    
    print(f"\n   Insgesamt {len(tracks)} Songs gefunden")
    
    song_list = []
    for item in tracks:
        track = item.get('track')
        if not track:
            continue
        artists = ", ".join([a["name"] for a in track.get("artists", [])])
        title = track.get("name", "Unknown")
        album = track.get("album", {}).get("name", "Unknown")
        duration_ms = track.get("duration_ms", 0)
        song_list.append({
            "title": title,
            "artist": artists,
            "album": album,
            "duration_ms": duration_ms
        })
    return song_list

def search_and_download(song, save_dir):
    artist = clean(song["artist"])
    title = clean(song["title"])
    
    # Prüfe, ob der Song bereits existiert
    if file_exists(save_dir, artist, title):
        print(f"\n→ Überspringe: {artist} - {title} (bereits vorhanden)")
        return "skipped"
    
    # yt-dlp Optionen mit dynamischem Speicherort
    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "0",
        }],
        "outtmpl": os.path.join(save_dir, "%(artist)s - %(track)s [%(id)s].%(ext)s"),
        "quiet": True,
        "no_warnings": True,
        "continuedl": True,
        "retries": 10,
        "default_search": "ytsearch5",
    }
    
    # Mehrere Such-Strategien – in Reihenfolge der Priorität
    search_variants = [
        f'"{title}" "{artist}" "Topic" OR "official audio" OR "audio" OR "vevo" OR "lyrics video" OR "album version"',
        f'"{artist}" "{title}" "Provided to YouTube" OR "Topic" OR "Auto-generated by YouTube."',
        f'"{title}" "{artist}" official',
        f'"{artist} - {title}" audio',
        f'"{title}" "{artist}"',
    ]
    
    print(f"\n→ Suche: {artist} - {title}")
    
    for query in search_variants:
        try:
            search_str = f"ytsearchdate5:{quote(query)}"
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(search_str, download=False)
                if not info.get("entries"):
                    continue
                
                entry = info["entries"][0]
                url = entry["url"]
                real_title = entry.get("title", title)
                
                if "topic" in real_title.lower() or "provided to youtube" in real_title.lower():
                    print("   → Treffer mit Topic / Provided → wahrscheinlich Album-Version!")
                
                print(f"   → Download von: {real_title}")
                ydl.download([url])
                return True
        except Exception as e:
            print(f"   Fehlgeschlagen mit Query '{query}': {e}")
            continue
    
    print("   → Kein guter Treffer gefunden.")
    return False

# ─── Hauptprogramm ───────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("   Spotify Playlist Downloader")
    print("=" * 60)
    
    playlist_url = input("\nSpotify Playlist Link einfügen: ").strip()
    
    if "spotify.com/playlist/" not in playlist_url:
        print("Das sieht nicht nach einem gültigen Spotify-Playlist-Link aus.")
    else:
        print("\nLade Playlist-Metadaten ...")
        
        # Hole Playlist-Info und Songs
        try:
            playlist_info = get_playlist_info(playlist_url)
            playlist_name = playlist_info["name"]
            
            # Erstelle Playlist-Ordner
            save_dir = os.path.join(BASE_SAVE_DIR, playlist_name)
            os.makedirs(save_dir, exist_ok=True)
            
            # Hole alle Songs
            songs = get_playlist_tracks(playlist_url)
        except Exception as e:
            print("\n" + "="*60)
            print("   ❌ FEHLER beim Laden der Playlist")
            print("="*60)
            print(f"\nFehlertyp: {type(e).__name__}")
            print(f"Fehlermeldung: {str(e)}")
            
            # Zeige vollständigen Traceback
            print("\n--- Vollständiger Fehler-Traceback ---")
            traceback.print_exc()
            print("\n" + "="*60)
            
            error_msg = str(e)
            
            if "403" in error_msg or "Forbidden" in error_msg:
                print("\n⚠️  HTTP 403 Forbidden - Was bedeutet das?")
                print("   Die Spotify API blockiert den Zugriff auf diese Playlist.\n")
                print("🔍 Mögliche Ursachen:")
                print("   1. Playlist ist privat (auch wenn sie für dich sichtbar ist)")
                print("   2. Du bist nicht der Besitzer der Playlist")
                print("   3. API-App im Development Mode hat eingeschränkte Rechte")
                print("   4. Spotify API-Berechtigungen sind nicht ausreichend\n")
                print("🔧 Lösungsvorschläge:")
                print("   ✓ Erstelle eine EIGENE Playlist in deinem Spotify-Account")
                print("   ✓ Stelle sicher, dass die Playlist 'Öffentlich' ist")
                print("   ✓ Kopiere Songs in deine eigene Playlist und lade diese herunter")
                print("   ✓ Gehe zu https://developer.spotify.com/dashboard")
                print("     und überprüfe die App-Einstellungen")
            elif "401" in error_msg or "Unauthorized" in error_msg:
                print("\n⚠️  HTTP 401 Unauthorized - API-Credentials ungültig!")
                print("   • Client ID oder Client Secret sind falsch")
                print("   • Überprüfe die .env Datei")
            elif "404" in error_msg or "Not Found" in error_msg:
                print("\n⚠️  HTTP 404 Not Found - Playlist existiert nicht!")
                print("   • Die Playlist-URL ist ungültig oder wurde gelöscht")
                print("   • Überprüfe die URL")
            elif "429" in error_msg or "Too Many Requests" in error_msg:
                print("\n⚠️  HTTP 429 Too Many Requests - API-Limit erreicht!")
                print("   • Zu viele Anfragen in kurzer Zeit")
                print("   • Warte ein paar Minuten und versuche es erneut")
            else:
                print("\n⚠️  Unbekannter Fehler")
                print("   • Keine Internetverbindung?")
                print("   • Spotify API hat ein Problem?")
                print("   • Siehe Traceback oben für Details")
            
            print("\n" + "="*60)
            input("\nDrücke Enter zum Beenden...")
            exit(1)
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