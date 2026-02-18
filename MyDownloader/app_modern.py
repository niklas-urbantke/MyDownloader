"""
🎵 Ultimate Music & Video Downloader - Modern UI
Mit CustomTkinter für ein modernes, schönes Design
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import re
import yt_dlp
import zipfile
import shutil
import glob
import json
from threading import Thread
from urllib.parse import urlparse, parse_qs
import queue
from datetime import datetime
import subprocess
import sys
import urllib.request
import time

# Queue für asynchrone Kommunikation
message_queue = queue.Queue()
progress_queue = queue.Queue()
detailed_progress_queue = queue.Queue()
error_queue = queue.Queue()
download_running = False
download_queue = queue.Queue()

# Node.js Verwaltung
NODEJS_VERSION = "20.11.0"
NODEJS_DIR = os.path.join(os.getcwd(), "nodejs_runtime")

# Einstellungen
SETTINGS_FILE = "settings.json"
HISTORY_FILE = "download_history.json"

def load_settings():
    """Lädt gespeicherte Einstellungen"""
    default_settings = {
        "download_folder": os.path.join(os.getcwd(), "Songs"),
        "audio_format": "mp3",
        "audio_quality": "0",
        "download_subtitles": False,
        "subtitle_language": "de,en",
        "speed_limit": "",
        "theme": "dark",
        "auto_queue": False,
        "embed_thumbnail": True,
        "embed_metadata": True,
        "keep_video": False
    }
    
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
                default_settings.update(loaded)
        except Exception as e:
            log_message(f"⚠️ Einstellungen konnten nicht geladen werden: {e}")
    
    return default_settings

def save_settings(settings):
    """Speichert Einstellungen"""
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
    except Exception as e:
        log_message(f"⚠️ Einstellungen konnten nicht gespeichert werden: {e}")

def load_history():
    """Lädt Download-History"""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_history(history):
    """Speichert Download-History"""
    try:
        history = history[-100:]
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=4, ensure_ascii=False)
    except Exception as e:
        log_message(f"⚠️ History konnte nicht gespeichert werden: {e}")

def add_to_history(url, title, timestamp=None):
    """Fügt Eintrag zur History hinzu"""
    history = load_history()
    history.append({
        'url': url,
        'title': title,
        'timestamp': timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    save_history(history)

def clean(text):
    """Entfernt unerlaubte Zeichen aus Dateinamen"""
    return re.sub(r'[<>:"/\\|?*]', '', text)

def check_and_setup_nodejs():
    """Prüft und installiert Node.js automatisch für yt-dlp JavaScript Runtime"""
    log_message("🔍 Prüfe Node.js JavaScript Runtime...")
    
    # Prüfe ob Node.js im System verfügbar ist
    nodejs_path = shutil.which("node")
    if nodejs_path:
        try:
            result = subprocess.run([nodejs_path, "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip()
                log_message(f"✅ Node.js gefunden (System): {version}")
                return True
        except:
            pass
    
    # Prüfe ob portable Version existiert
    local_node = os.path.join(NODEJS_DIR, "node.exe")
    if os.path.exists(local_node):
        try:
            result = subprocess.run([local_node, "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip()
                # Zum PATH hinzufügen
                os.environ["PATH"] = NODEJS_DIR + os.pathsep + os.environ.get("PATH", "")
                log_message(f"✅ Node.js gefunden (Portable): {version}")
                return True
        except:
            pass
    
    # Node.js nicht gefunden - Download starten
    log_message("⚠️ Node.js nicht gefunden - lade portable Version herunter...")
    return download_nodejs()

def download_nodejs():
    """Lädt portable Node.js Version herunter"""
    try:
        # Portable Node.js URL
        url = f"https://nodejs.org/dist/v{NODEJS_VERSION}/node-v{NODEJS_VERSION}-win-x64.zip"
        zip_path = os.path.join(os.getcwd(), "nodejs.zip")
        
        log_message(f"📥 Lade Node.js v{NODEJS_VERSION} herunter...")
        log_message("⏳ Dies kann einige Minuten dauern...")
        
        # Download mit Progress
        def download_progress(count, block_size, total_size):
            if total_size > 0:
                percent = int(count * block_size * 100 / total_size)
                if percent % 10 == 0 and percent > 0:
                    log_message(f"📊 Download: {percent}%")
        
        urllib.request.urlretrieve(url, zip_path, reporthook=download_progress)
        log_message("✅ Download abgeschlossen")
        
        # Entpacken
        log_message("📦 Entpacke Node.js...")
        os.makedirs(NODEJS_DIR, exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Extrahiere alle Dateien
            for member in zip_ref.namelist():
                # Entferne den obersten Ordner-Namen
                target_path = os.path.join(NODEJS_DIR, *member.split('/')[1:])
                if member.endswith('/'):
                    os.makedirs(target_path, exist_ok=True)
                else:
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    with zip_ref.open(member) as source, open(target_path, 'wb') as target:
                        shutil.copyfileobj(source, target)
        
        # Cleanup
        os.remove(zip_path)
        
        # Zum PATH hinzufügen
        os.environ["PATH"] = NODEJS_DIR + os.pathsep + os.environ.get("PATH", "")
        
        log_message("✅ Node.js erfolgreich installiert!")
        log_message("✅ JavaScript Runtime ist jetzt verfügbar")
        return True
        
    except Exception as e:
        log_message(f"❌ Fehler beim Installieren von Node.js: {e}")
        log_message("⚠️ YouTube-Downloads könnten eingeschränkt sein")
        log_message("💡 Installiere Node.js manuell von https://nodejs.org")
        return False

def check_ffmpeg():
    """Prüft, ob FFmpeg verfügbar ist"""
    log_message("🔍 Prüfe FFmpeg...")
    
    local_ffmpeg = os.path.join(os.getcwd(), "ffmpeg", "bin")
    local_ffmpeg_exe = os.path.join(local_ffmpeg, "ffmpeg.exe")
    
    if os.path.exists(local_ffmpeg_exe):
        os.environ["PATH"] = local_ffmpeg + os.pathsep + os.environ.get("PATH", "")
        log_message("✅ FFmpeg gefunden (Portable Version)")
        return True
    
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        log_message("✅ FFmpeg gefunden (System)")
        return True
    
    log_message("⚠️ FFmpeg nicht gefunden - manche Features funktionieren nicht")
    return False

def parse_video_title(title):
    """Extrahiert Künstler und Titel aus YouTube-Videonamen"""
    original = title
    
    patterns = [
        r'\s*\(official.*?\)', r'\s*\[official.*?\]',
        r'\s*\(HD\)', r'\s*\[HD\]', r'\s*\(4K\)', r'\s*\[4K\]',
        r'\s*\(Audio\)', r'\s*\[Audio\]',
        r'\s*\(Lyrics\)', r'\s*\[Lyrics\]',
        r'\s*\(Lyric Video\)', r'\s*\[Lyric Video\]',
        r'\s*\(Music Video\)', r'\s*\[Music Video\]',
    ]
    
    for pattern in patterns:
        title = re.sub(pattern, '', title, flags=re.IGNORECASE)
    
    title = title.strip()
    
    if ' - ' in title:
        parts = title.split(' - ', 1)
        return parts[0].strip(), parts[1].strip()
    
    return "Unknown Artist", original

def get_video_info(url):
    """Lädt Video-Informationen ohne Download"""
    ydl_opts = {'quiet': True, 'no_warnings': True}
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                'title': info.get('title', 'Unbekannt'),
                'duration': info.get('duration', 0),
                'thumbnail': info.get('thumbnail', ''),
                'uploader': info.get('uploader', 'Unbekannt'),
                'view_count': info.get('view_count', 0),
                'url': url
            }
    except Exception as e:
        log_message(f"❌ Fehler beim Laden der Video-Info: {e}")
        return None

def get_youtube_playlist(url):
    """Lädt YouTube-Playlist-Informationen"""
    log_message("📋 Lade Playlist-Informationen...")
    
    parsed = urlparse(url)
    if "list=" in url:
        query_params = parse_qs(parsed.query)
        playlist_id = query_params.get("list", [None])[0]
        if playlist_id:
            url = f"https://www.youtube.com/playlist?list={playlist_id}"
    
    ydl_opts = {'extract_flat': True, 'quiet': True, 'yes_playlist': True}
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            if 'entries' not in info:
                return None
            
            playlist_name = info.get('title', 'YouTube Playlist')
            songs = []
            
            for entry in info['entries']:
                if entry:
                    video_title = entry.get('title', '')
                    video_url = f"https://www.youtube.com/watch?v={entry['id']}"
                    artist, title = parse_video_title(video_title)
                    
                    songs.append({
                        'artist': artist,
                        'title': title,
                        'original_url': video_url,
                        'original_title': video_title
                    })
            
            log_message(f"✅ Playlist geladen: {playlist_name} ({len(songs)} Songs)")
            return {'name': playlist_name, 'songs': songs, 'url': url}
    except Exception as e:
        log_message(f"❌ Fehler beim Laden der Playlist: {e}")
        return None

def download_single(url, save_dir, settings, idx=1, total=1):
    """Lädt einzelnen Song/Video herunter mit detailliertem Progress"""
    progress_queue.put({'current': idx, 'total': total, 'song': url})
    
    log_message(f"🔍 [{idx}/{total}] Verarbeite: {url}")
    
    title = "Unknown"
    duration = 0
    filesize = 0
    
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'Unknown')
            duration = info.get('duration', 0)
            # Geschätzte Dateigröße
            if 'filesize' in info:
                filesize = info['filesize']
            elif 'filesize_approx' in info:
                filesize = info['filesize_approx']
    except Exception as e:
        error_msg = f"Fehler beim Laden der Video-Info: {str(e)}"
        log_message(f"⚠️ [{idx}/{total}] {error_msg}")
        error_queue.put({'index': idx, 'title': title, 'error': error_msg, 'url': url})
    
    output_template = os.path.join(save_dir, "%(title)s.%(ext)s")
    
    # Progress Hook für detaillierte Anzeige
    def progress_hook(d):
        if d['status'] == 'downloading':
            # Extrahiere Details
            downloaded = d.get('downloaded_bytes', 0)
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            speed = d.get('speed', 0)
            eta = d.get('eta', 0)
            percent = d.get('_percent_str', '0%')
            
            # Formatiere Werte
            speed_str = f"{speed / 1024 / 1024:.2f} MB/s" if speed else "? MB/s"
            
            if total_bytes > 0:
                downloaded_mb = downloaded / 1024 / 1024
                total_mb = total_bytes / 1024 / 1024
                size_str = f"{downloaded_mb:.1f}/{total_mb:.1f} MB"
            else:
                downloaded_mb = downloaded / 1024 / 1024
                size_str = f"{downloaded_mb:.1f} MB"
            
            eta_str = f"{eta}s" if eta else "?"
            
            # Sende detaillierte Progress-Info
            detailed_progress_queue.put({
                'index': idx,
                'total': total,
                'title': title,
                'percent': percent.strip(),
                'speed': speed_str,
                'size': size_str,
                'eta': eta_str,
                'status': 'downloading'
            })
        
        elif d['status'] == 'finished':
            filename = d.get('filename', '')
            total_bytes = d.get('total_bytes', 0)
            total_mb = total_bytes / 1024 / 1024 if total_bytes else 0
            
            detailed_progress_queue.put({
                'index': idx,
                'total': total,
                'title': title,
                'status': 'processing',
                'message': f"Download abgeschlossen ({total_mb:.1f} MB), verarbeite..."
            })
    
    ydl_opts = {
        "outtmpl": output_template,
        "quiet": False,
        "no_warnings": False,
        "continuedl": True,
        "retries": 10,
        "progress_hooks": [progress_hook],
    }
    
    if settings.get('audio_format') and settings['audio_format'] != 'none':
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': settings['audio_format'],
            'preferredquality': settings.get('audio_quality', '0'),
        }]
        
        if settings.get('embed_thumbnail'):
            ydl_opts['postprocessors'].append({'key': 'EmbedThumbnail'})
            ydl_opts['writethumbnail'] = True
        
        if settings.get('embed_metadata'):
            ydl_opts['postprocessors'].append({'key': 'FFmpegMetadata'})
    else:
        ydl_opts['format'] = 'bestvideo+bestaudio/best'
    
    if settings.get('download_subtitles'):
        ydl_opts['writesubtitles'] = True
        ydl_opts['subtitleslangs'] = settings.get('subtitle_language', 'de,en').split(',')
        ydl_opts['subtitlesformat'] = 'srt'
    
    if settings.get('speed_limit'):
        try:
            limit = int(settings['speed_limit'])
            ydl_opts['ratelimit'] = limit * 1024 * 1024
        except:
            pass
    
    try:
        log_message(f"📥 [{idx}/{total}] Download startet: {title}")
        if duration > 0:
            minutes = duration // 60
            seconds = duration % 60
            log_message(f"⏱️ Dauer: {minutes}:{seconds:02d}")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        log_message(f"✅ [{idx}/{total}] Erfolgreich: {title}")
        detailed_progress_queue.put({
            'index': idx,
            'total': total,
            'title': title,
            'status': 'completed'
        })
        add_to_history(url, title)
        return True
        
    except Exception as e:
        error_msg = str(e)
        # Detaillierte Fehleranalyse
        if "HTTP Error 403" in error_msg:
            error_detail = "Zugriff verweigert (403) - Video könnte geschützt sein"
        elif "HTTP Error 404" in error_msg:
            error_detail = "Video nicht gefunden (404) - URL prüfen"
        elif "Video unavailable" in error_msg:
            error_detail = "Video nicht verfügbar - evtl. gelöscht oder privat"
        elif "Sign in to confirm" in error_msg:
            error_detail = "Altersbeschränkung - Login erforderlich"
        elif "This video is DRM protected" in error_msg:
            error_detail = "DRM-geschützt - Download nicht möglich"
        else:
            error_detail = error_msg
        
        log_message(f"❌ [{idx}/{total}] FEHLER: {title}")
        log_message(f"   ⚠️ Details: {error_detail}")
        log_message(f"   🔗 URL: {url}")
        
        error_queue.put({
            'index': idx,
            'title': title,
            'error': error_detail,
            'url': url,
            'full_error': error_msg
        })
        
        detailed_progress_queue.put({
            'index': idx,
            'total': total,
            'title': title,
            'status': 'error',
            'error': error_detail
        })
        
        return False

def download_playlist_thread(playlist_data, settings):
    """Thread-Funktion für Playlist-Downloads mit detaillierter Statistik"""
    global download_running
    download_running = True
    
    playlist_name = playlist_data['name']
    songs = playlist_data['songs']
    
    base_dir = os.path.join(settings['download_folder'], clean(playlist_name))
    os.makedirs(base_dir, exist_ok=True)
    
    log_message(f"\n{'='*60}")
    log_message(f"▶️ Download startet: {playlist_name}")
    log_message(f"📊 Anzahl Songs: {len(songs)}")
    log_message(f"📁 Speicherort: {base_dir}")
    log_message(f"{'='*60}\n")
    
    success_count = 0
    error_count = 0
    start_time = time.time()
    errors_list = []
    
    for idx, song in enumerate(songs, 1):
        if not download_running:
            log_message("\n⚠️ Download abgebrochen!")
            break
        
        result = download_single(song['original_url'], base_dir, settings, idx, len(songs))
        if result:
            success_count += 1
        else:
            error_count += 1
            # Sammle Fehler
            while not error_queue.empty():
                error_info = error_queue.get()
                if error_info['index'] == idx:
                    errors_list.append(error_info)
    
    elapsed_time = time.time() - start_time
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)
    
    log_message(f"\n{'='*60}")
    log_message(f"✅ Download abgeschlossen!")
    log_message(f"✅ Erfolgreich: {success_count}/{len(songs)}")
    log_message(f"❌ Fehler: {error_count}/{len(songs)}")
    log_message(f"⏱️ Gesamtzeit: {minutes}m {seconds}s")
    log_message(f"📁 Speicherort: {base_dir}")
    
    # Detaillierte Fehler-Übersicht
    if errors_list:
        log_message(f"\n⚠️ FEHLER-DETAILS ({len(errors_list)}):")
        log_message("-" * 60)
        for err in errors_list:
            log_message(f"  {err['index']}. {err['title']}")
            log_message(f"     Grund: {err['error']}")
            log_message(f"     URL: {err['url']}")
            log_message("")
    
    log_message(f"{'='*60}\n")
    
    add_to_history(playlist_data.get('url', ''), playlist_name)
    download_running = False
    progress_queue.put({'completed': True, 'success': success_count, 'errors': error_count})

def download_queue_thread(settings):
    """Thread-Funktion für Queue-Downloads mit detaillierter Statistik"""
    global download_running
    download_running = True
    
    items = []
    while not download_queue.empty():
        items.append(download_queue.get())
    
    if not items:
        log_message("⚠️ Queue ist leer!")
        download_running = False
        progress_queue.put({'completed': True, 'success': 0, 'errors': 0})
        return
    
    base_dir = settings['download_folder']
    os.makedirs(base_dir, exist_ok=True)
    
    log_message(f"\n{'='*60}")
    log_message(f"▶️ Queue-Download startet")
    log_message(f"📊 Anzahl Items: {len(items)}")
    log_message(f"{'='*60}\n")
    
    success_count = 0
    error_count = 0
    start_time = time.time()
    errors_list = []
    
    for idx, url in enumerate(items, 1):
        if not download_running:
            log_message("\n⚠️ Download abgebrochen!")
            break
        
        result = download_single(url, base_dir, settings, idx, len(items))
        if result:
            success_count += 1
        else:
            error_count += 1
            # Sammle Fehler
            while not error_queue.empty():
                error_info = error_queue.get()
                if error_info['index'] == idx:
                    errors_list.append(error_info)
    
    elapsed_time = time.time() - start_time
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)
    
    log_message(f"\n{'='*60}")
    log_message(f"✅ Queue-Download abgeschlossen!")
    log_message(f"✅ Erfolgreich: {success_count}/{len(items)}")
    log_message(f"❌ Fehler: {error_count}/{len(items)}")
    log_message(f"⏱️ Gesamtzeit: {minutes}m {seconds}s")
    
    # Detaillierte Fehler-Übersicht
    if errors_list:
        log_message(f"\n⚠️ FEHLER-DETAILS ({len(errors_list)}):")
        log_message("-" * 60)
        for err in errors_list:
            log_message(f"  {err['index']}. {err['title']}")
            log_message(f"     Grund: {err['error']}")
            log_message(f"     URL: {err['url']}")
            log_message("")
    
    log_message(f"{'='*60}\n")
    
    download_running = False
    progress_queue.put({'completed': True, 'success': success_count, 'errors': error_count})

def log_message(msg):
    """Fügt Nachricht zur Queue hinzu"""
    message_queue.put(msg)


class ModernDownloaderApp(ctk.CTk):
    """Moderne Downloader-App mit CustomTkinter"""
    
    def __init__(self):
        super().__init__()
        
        # Fenster-Konfiguration
        self.title("🎵 Ultimate Music & Video Downloader")
        self.geometry("1300x900")
        self.minsize(1000, 700)
        
        # Einstellungen laden
        self.settings = load_settings()
        
        # Theme setzen
        ctk.set_appearance_mode(self.settings.get('theme', 'dark'))
        ctk.set_default_color_theme("blue")
        
        # Daten
        self.playlist_data = None
        self.preview_info = None
        
        # UI erstellen
        self.create_ui()
        
        # Umgebungs-Checks (Node.js und FFmpeg)
        Thread(target=self._check_environment, daemon=True).start()
        
        # Queue Processing
        self.process_queues()
    
    def _check_environment(self):
        """Pr\u00fcft Node.js und FFmpeg"""
        check_and_setup_nodejs()
        check_ffmpeg()
    
    def create_ui(self):
        """Erstellt die moderne UI"""
        
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent", height=100)
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        header_frame.pack_propagate(False)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="🎵 Music & Video Downloader",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title_label.pack(side="left", pady=10)
        
        # Theme Toggle
        self.theme_switch = ctk.CTkSwitch(
            header_frame,
            text="🌙 Dark Mode",
            command=self.toggle_theme,
            font=ctk.CTkFont(size=14)
        )
        self.theme_switch.pack(side="right", pady=10, padx=10)
        if self.settings.get('theme') == 'dark':
            self.theme_switch.select()
        
        # Tabs
        self.tabview = ctk.CTkTabview(self, height=700)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Tab erstellen
        self.tab_download = self.tabview.add("📥 Download")
        self.tab_queue = self.tabview.add("📑 Queue")
        self.tab_history = self.tabview.add("📜 History")
        self.tab_settings = self.tabview.add("⚙️ Einstellungen")
        
        # Tabs befüllen
        self.create_download_tab()
        self.create_queue_tab()
        self.create_history_tab()
        self.create_settings_tab()
        
        # Status Bar
        self.status_frame = ctk.CTkFrame(self, height=40, fg_color="transparent")
        self.status_frame.pack(fill="x", padx=20, pady=(0, 15))
        self.status_frame.pack_propagate(False)
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="✅ Bereit",
            font=ctk.CTkFont(size=12),
            anchor="w"
        )
        self.status_label.pack(side="left", fill="x", expand=True)
    
    def create_download_tab(self):
        """Erstellt den Download-Tab"""
        tab = self.tab_download
        
        # URL Input Section
        url_frame = ctk.CTkFrame(tab)
        url_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            url_frame,
            text="🔗 Video/Playlist URL",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))
        
        input_frame = ctk.CTkFrame(url_frame, fg_color="transparent")
        input_frame.pack(fill="x", padx=15, pady=(5, 15))
        
        self.url_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="YouTube URL hier eingeben...",
            height=45,
            font=ctk.CTkFont(size=14)
        )
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkButton(
            input_frame,
            text="👁️ Vorschau",
            command=self.show_preview,
            height=45,
            width=130,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left")
        
        # Buttons
        btn_frame = ctk.CTkFrame(url_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        self.load_playlist_btn = ctk.CTkButton(
            btn_frame,
            text="📋 Playlist laden",
            command=self.load_playlist,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#3B82F6",
            hover_color="#2563EB"
        )
        self.load_playlist_btn.pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            btn_frame,
            text="⬇️ Einzeln Download",
            command=self.download_single_video,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#10B981",
            hover_color="#059669"
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            btn_frame,
            text="➕ Zur Queue",
            command=self.add_to_queue,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#F59E0B",
            hover_color="#D97706"
        ).pack(side="left")
        
        # Info/Preview
        info_frame = ctk.CTkFrame(tab)
        info_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        ctk.CTkLabel(
            info_frame,
            text="ℹ️ Informationen",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))
        
        self.info_textbox = ctk.CTkTextbox(
            info_frame,
            height=150,
            font=ctk.CTkFont(size=13)
        )
        self.info_textbox.pack(fill="both", expand=True, padx=15, pady=(5, 15))
        self.info_textbox.insert("1.0", "Gib eine URL ein und klicke auf 'Vorschau' für Details...")
        self.info_textbox.configure(state="disabled")
        
        # Download Controls
        control_frame = ctk.CTkFrame(tab)
        control_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkLabel(
            control_frame,
            text="🎛️ Download-Steuerung",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 10))
        
        # Folder Selection
        folder_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        folder_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        ctk.CTkLabel(
            folder_frame,
            text="📁 Download-Ordner:",
            font=ctk.CTkFont(size=13)
        ).pack(side="left", padx=(0, 10))
        
        self.folder_label = ctk.CTkLabel(
            folder_frame,
            text=self.settings['download_folder'],
            font=ctk.CTkFont(size=12),
            anchor="w"
        )
        self.folder_label.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkButton(
            folder_frame,
            text="🗂️ Ändern",
            command=self.select_download_folder,
            height=35,
            width=100,
            font=ctk.CTkFont(size=13)
        ).pack(side="left")
        
        # Action Buttons
        btn_frame2 = ctk.CTkFrame(control_frame, fg_color="transparent")
        btn_frame2.pack(fill="x", padx=15, pady=(0, 15))
        
        self.start_download_btn = ctk.CTkButton(
            btn_frame2,
            text="▶️ Playlist Download starten",
            command=self.start_playlist_download,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#10B981",
            hover_color="#059669",
            state="disabled"
        )
        self.start_download_btn.pack(side="left", padx=(0, 10))
        
        self.stop_download_btn = ctk.CTkButton(
            btn_frame2,
            text="⏹️ Abbrechen",
            command=self.stop_download,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#EF4444",
            hover_color="#DC2626",
            state="disabled"
        )
        self.stop_download_btn.pack(side="left")
        
        # Progress
        progress_frame = ctk.CTkFrame(tab)
        progress_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkLabel(
            progress_frame,
            text="📊 Fortschritt",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))
        
        self.progress_label = ctk.CTkLabel(
            progress_frame,
            text="Bereit",
            font=ctk.CTkFont(size=13),
            anchor="w"
        )
        self.progress_label.pack(anchor="w", padx=15, pady=(5, 5))
        
        self.progress_bar = ctk.CTkProgressBar(progress_frame, height=15)
        self.progress_bar.pack(fill="x", padx=15, pady=(5, 5))
        self.progress_bar.set(0)
        
        # Detaillierte Download-Info (neu!)
        self.detail_progress_label = ctk.CTkLabel(
            progress_frame,
            text="",
            font=ctk.CTkFont(family="Consolas", size=11),
            anchor="w",
            text_color="#10B981"
        )
        self.detail_progress_label.pack(anchor="w", padx=15, pady=(0, 15))
        
        # Log
        log_frame = ctk.CTkFrame(tab)
        log_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        ctk.CTkLabel(
            log_frame,
            text="📝 Aktivität",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))
        
        self.log_textbox = ctk.CTkTextbox(
            log_frame,
            font=ctk.CTkFont(family="Consolas", size=11)
        )
        self.log_textbox.pack(fill="both", expand=True, padx=15, pady=(5, 15))
        self.log_textbox.insert("1.0", "=== Ultimate Music & Video Downloader ===\n")
        self.log_textbox.configure(state="disabled")
    
    def create_queue_tab(self):
        """Erstellt den Queue-Tab"""
        tab = self.tab_queue
        
        # Controls
        control_frame = ctk.CTkFrame(tab)
        control_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            control_frame,
            text="🎛️ Queue-Steuerung",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 10))
        
        btn_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        ctk.CTkButton(
            btn_frame,
            text="📄 Aus Datei importieren",
            command=self.import_from_file,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            btn_frame,
            text="📋 Aus Zwischenablage",
            command=self.import_from_clipboard,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            btn_frame,
            text="🗑️ Queue leeren",
            command=self.clear_queue,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#EF4444",
            hover_color="#DC2626"
        ).pack(side="left", padx=(0, 10))
        
        self.start_queue_btn = ctk.CTkButton(
            btn_frame,
            text="▶️ Queue starten",
            command=self.start_queue_download,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#10B981",
            hover_color="#059669"
        )
        self.start_queue_btn.pack(side="left")
        
        # Queue List
        list_frame = ctk.CTkFrame(tab)
        list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        ctk.CTkLabel(
            list_frame,
            text="📋 Queue-Einträge",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))
        
        self.queue_textbox = ctk.CTkTextbox(
            list_frame,
            font=ctk.CTkFont(size=12)
        )
        self.queue_textbox.pack(fill="both", expand=True, padx=15, pady=(5, 15))
        self.queue_textbox.configure(state="disabled")
        self.update_queue_display()
    
    def create_history_tab(self):
        """Erstellt den History-Tab"""
        tab = self.tab_history
        
        # Controls
        control_frame = ctk.CTkFrame(tab)
        control_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            control_frame,
            text="📜 Download-Verlauf",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 10))
        
        btn_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        ctk.CTkButton(
            btn_frame,
            text="🔄 Aktualisieren",
            command=self.refresh_history,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            btn_frame,
            text="🗑️ History löschen",
            command=self.clear_history,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#EF4444",
            hover_color="#DC2626"
        ).pack(side="left")
        
        # History Display
        history_frame = ctk.CTkFrame(tab)
        history_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.history_textbox = ctk.CTkTextbox(
            history_frame,
            font=ctk.CTkFont(size=12)
        )
        self.history_textbox.pack(fill="both", expand=True, padx=15, pady=15)
        self.refresh_history()
    
    def create_settings_tab(self):
        """Erstellt den Einstellungs-Tab"""
        tab = self.tab_settings
        
        # Scrollable Frame
        scrollable = ctk.CTkScrollableFrame(tab)
        scrollable.pack(fill="both", expand=True, padx=20, pady=20)
        
        # System Status (neu!)
        system_frame = ctk.CTkFrame(scrollable)
        system_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            system_frame,
            text="🔧 System-Status",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 10))
        
        # Node.js Status
        self.nodejs_status_label = ctk.CTkLabel(
            system_frame,
            text="⏳ Prüfe Node.js...",
            font=ctk.CTkFont(size=13),
            anchor="w"
        )
        self.nodejs_status_label.pack(anchor="w", padx=15, pady=5)
        
        # FFmpeg Status
        self.ffmpeg_status_label = ctk.CTkLabel(
            system_frame,
            text="⏳ Prüfe FFmpeg...",
            font=ctk.CTkFont(size=13),
            anchor="w"
        )
        self.ffmpeg_status_label.pack(anchor="w", padx=15, pady=(5, 15))
        
        # Audio Settings
        audio_frame = ctk.CTkFrame(scrollable)
        audio_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            audio_frame,
            text="🎵 Audio-Einstellungen",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 10))
        
        # Audio Format
        format_frame = ctk.CTkFrame(audio_frame, fg_color="transparent")
        format_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(
            format_frame,
            text="Format:",
            font=ctk.CTkFont(size=13),
            width=150,
            anchor="w"
        ).pack(side="left")
        
        self.audio_format_var = ctk.StringVar(value=self.settings.get('audio_format', 'mp3'))
        ctk.CTkOptionMenu(
            format_frame,
            values=['mp3', 'm4a', 'opus', 'flac', 'wav', 'none (Video)'],
            variable=self.audio_format_var,
            font=ctk.CTkFont(size=13),
            width=200
        ).pack(side="left")
        
        # Audio Quality
        quality_frame = ctk.CTkFrame(audio_frame, fg_color="transparent")
        quality_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(
            quality_frame,
            text="Qualität:",
            font=ctk.CTkFont(size=13),
            width=150,
            anchor="w"
        ).pack(side="left")
        
        self.audio_quality_var = ctk.StringVar(value=self.settings.get('audio_quality', '0'))
        ctk.CTkOptionMenu(
            quality_frame,
            values=['0 (Beste)', '2', '5', '9 (Kleinste)'],
            variable=self.audio_quality_var,
            font=ctk.CTkFont(size=13),
            width=200
        ).pack(side="left")
        
        # Switches
        switch_frame = ctk.CTkFrame(audio_frame, fg_color="transparent")
        switch_frame.pack(fill="x", padx=15, pady=10)
        
        self.embed_thumbnail_var = ctk.BooleanVar(value=self.settings.get('embed_thumbnail', True))
        ctk.CTkSwitch(
            switch_frame,
            text="🖼️ Thumbnail einbetten",
            variable=self.embed_thumbnail_var,
            font=ctk.CTkFont(size=13)
        ).pack(anchor="w", pady=5)
        
        self.embed_metadata_var = ctk.BooleanVar(value=self.settings.get('embed_metadata', True))
        ctk.CTkSwitch(
            switch_frame,
            text="📝 Metadaten einbetten",
            variable=self.embed_metadata_var,
            font=ctk.CTkFont(size=13)
        ).pack(anchor="w", pady=5)
        
        # Subtitle Settings
        subtitle_frame = ctk.CTkFrame(scrollable)
        subtitle_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            subtitle_frame,
            text="💬 Untertitel-Einstellungen",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 10))
        
        self.download_subtitles_var = ctk.BooleanVar(value=self.settings.get('download_subtitles', False))
        ctk.CTkSwitch(
            subtitle_frame,
            text="📥 Untertitel herunterladen",
            variable=self.download_subtitles_var,
            font=ctk.CTkFont(size=13)
        ).pack(anchor="w", padx=15, pady=5)
        
        lang_frame = ctk.CTkFrame(subtitle_frame, fg_color="transparent")
        lang_frame.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(
            lang_frame,
            text="Sprachen:",
            font=ctk.CTkFont(size=13),
            width=150,
            anchor="w"
        ).pack(side="left")
        
        self.subtitle_language_var = ctk.StringVar(value=self.settings.get('subtitle_language', 'de,en'))
        ctk.CTkEntry(
            lang_frame,
            textvariable=self.subtitle_language_var,
            placeholder_text="z.B. de,en",
            width=200,
            font=ctk.CTkFont(size=13)
        ).pack(side="left")
        
        # Download Settings
        download_frame = ctk.CTkFrame(scrollable)
        download_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            download_frame,
            text="⚡ Download-Einstellungen",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 10))
        
        speed_frame = ctk.CTkFrame(download_frame, fg_color="transparent")
        speed_frame.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(
            speed_frame,
            text="Geschwindigkeit (MB/s):",
            font=ctk.CTkFont(size=13),
            width=200,
            anchor="w"
        ).pack(side="left")
        
        self.speed_limit_var = ctk.StringVar(value=self.settings.get('speed_limit', ''))
        ctk.CTkEntry(
            speed_frame,
            textvariable=self.speed_limit_var,
            placeholder_text="leer = unbegrenzt",
            width=150,
            font=ctk.CTkFont(size=13)
        ).pack(side="left")
        
        # Save Button
        save_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
        save_frame.pack(fill="x", pady=20)
        
        ctk.CTkButton(
            save_frame,
            text="💾 Einstellungen speichern",
            command=self.save_settings_gui,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#10B981",
            hover_color="#059669"
        ).pack(side="left", padx=(15, 10))
        
        ctk.CTkButton(
            save_frame,
            text="🔄 yt-dlp aktualisieren",
            command=self.update_ytdlp,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left")
    
    # Event Handlers
    def toggle_theme(self):
        """Wechselt zwischen Dark/Light Mode"""
        if self.theme_switch.get():
            ctk.set_appearance_mode("dark")
            self.settings['theme'] = 'dark'
        else:
            ctk.set_appearance_mode("light")
            self.settings['theme'] = 'light'
        save_settings(self.settings)
    
    def select_download_folder(self):
        """Ordner-Auswahl Dialog"""
        folder = filedialog.askdirectory(
            title="Download-Ordner auswählen",
            initialdir=self.settings['download_folder']
        )
        
        if folder:
            self.settings['download_folder'] = folder
            save_settings(self.settings)
            self.folder_label.configure(text=folder)
            self.add_log(f"📁 Download-Ordner geändert: {folder}")
            self.status_label.configure(text=f"📁 Download-Ordner: {folder}")
    
    def show_preview(self):
        """Zeigt Vorschau des Videos"""
        url = self.url_entry.get().strip()
        
        if not url:
            messagebox.showwarning("Fehler", "Bitte eine URL eingeben!")
            return
        
        self.status_label.configure(text="⏳ Lade Vorschau...")
        Thread(target=self._load_preview_thread, args=(url,), daemon=True).start()
    
    def _load_preview_thread(self, url):
        """Thread für Vorschau"""
        info = get_video_info(url)
        
        if info:
            self.preview_info = info
            
            info_text = f"""
📹 Titel: {info['title']}
👤 Uploader: {info['uploader']}
⏱️ Dauer: {info['duration'] // 60}:{info['duration'] % 60:02d}
👁️ Views: {info.get('view_count', 0):,}
🔗 URL: {info['url']}
"""
            
            self.info_textbox.configure(state="normal")
            self.info_textbox.delete("1.0", "end")
            self.info_textbox.insert("1.0", info_text.strip())
            self.info_textbox.configure(state="disabled")
            
            self.status_label.configure(text="✅ Vorschau geladen")
        else:
            messagebox.showerror("Fehler", "Vorschau konnte nicht geladen werden!")
            self.status_label.configure(text="❌ Fehler beim Laden")
    
    def load_playlist(self):
        """Lädt Playlist"""
        url = self.url_entry.get().strip()
        
        if not url:
            messagebox.showwarning("Fehler", "Bitte eine URL eingeben!")
            return
        
        self.load_playlist_btn.configure(state="disabled")
        self.status_label.configure(text="⏳ Lade Playlist...")
        
        Thread(target=self._load_playlist_thread, args=(url,), daemon=True).start()
    
    def _load_playlist_thread(self, url):
        """Thread für Playlist-Laden"""
        self.playlist_data = get_youtube_playlist(url)
        
        if self.playlist_data:
            info_text = f"""
📋 Playlist: {self.playlist_data['name']}
🎵 Anzahl Songs: {len(self.playlist_data['songs'])}
🔗 URL: {self.playlist_data.get('url', '')}

Songs (erste 10):
"""
            for idx, song in enumerate(self.playlist_data['songs'][:10], 1):
                info_text += f"{idx}. {song['artist']} - {song['title']}\n"
            
            if len(self.playlist_data['songs']) > 10:
                info_text += f"... und {len(self.playlist_data['songs']) - 10} weitere"
            
            self.info_textbox.configure(state="normal")
            self.info_textbox.delete("1.0", "end")
            self.info_textbox.insert("1.0", info_text.strip())
            self.info_textbox.configure(state="disabled")
            
            self.start_download_btn.configure(state="normal")
            self.status_label.configure(text=f"✅ Playlist geladen: {self.playlist_data['name']}")
        else:
            messagebox.showerror("Fehler", "Playlist konnte nicht geladen werden!")
            self.status_label.configure(text="❌ Fehler beim Laden")
        
        self.load_playlist_btn.configure(state="normal")
    
    def download_single_video(self):
        """Lädt einzelnes Video herunter"""
        url = self.url_entry.get().strip()
        
        if not url:
            messagebox.showwarning("Fehler", "Bitte eine URL eingeben!")
            return
        
        self.stop_download_btn.configure(state="normal")
        self.status_label.configure(text="▶️ Download läuft...")
        
        current_settings = self.get_current_settings()
        Thread(target=self._download_single_thread, args=(url, current_settings), daemon=True).start()
    
    def _download_single_thread(self, url, settings):
        """Thread für Einzel-Download"""
        global download_running
        download_running = True
        
        download_single(url, settings['download_folder'], settings, 1, 1)
        
        download_running = False
        progress_queue.put({'completed': True})
        
        self.stop_download_btn.configure(state="disabled")
    
    def add_to_queue(self):
        """Fügt URL zur Queue hinzu"""
        url = self.url_entry.get().strip()
        
        if not url:
            messagebox.showwarning("Fehler", "Bitte eine URL eingeben!")
            return
        
        download_queue.put(url)
        self.add_log(f"➕ Zur Queue hinzugefügt: {url}")
        self.update_queue_display()
        self.status_label.configure(text=f"✅ {download_queue.qsize()} Einträge in Queue")
        self.url_entry.delete(0, "end")
    
    def start_playlist_download(self):
        """Startet Playlist-Download"""
        if not self.playlist_data:
            messagebox.showwarning("Fehler", "Bitte zuerst eine Playlist laden!")
            return
        
        self.start_download_btn.configure(state="disabled")
        self.load_playlist_btn.configure(state="disabled")
        self.stop_download_btn.configure(state="normal")
        self.progress_bar.set(0)
        self.status_label.configure(text="▶️ Playlist-Download läuft...")
        
        current_settings = self.get_current_settings()
        Thread(target=download_playlist_thread, args=(self.playlist_data, current_settings), daemon=True).start()
    
    def start_queue_download(self):
        """Startet Queue-Download"""
        if download_queue.empty():
            messagebox.showwarning("Fehler", "Queue ist leer!")
            return
        
        self.start_queue_btn.configure(state="disabled")
        self.stop_download_btn.configure(state="normal")
        self.status_label.configure(text="▶️ Queue-Download läuft...")
        
        current_settings = self.get_current_settings()
        Thread(target=download_queue_thread, args=(current_settings,), daemon=True).start()
    
    def stop_download(self):
        """Stoppt Download"""
        global download_running
        download_running = False
        self.stop_download_btn.configure(state="disabled")
        self.status_label.configure(text="⏹️ Download wird abgebrochen...")
    
    def import_from_file(self):
        """Importiert URLs aus Textdatei"""
        filename = filedialog.askopenfilename(
            title="Textdatei mit URLs auswählen",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                count = 0
                for line in lines:
                    url = line.strip()
                    if url and url.startswith('http'):
                        download_queue.put(url)
                        count += 1
                
                self.add_log(f"📄 {count} URLs aus Datei importiert")
                self.update_queue_display()
                self.status_label.configure(text=f"✅ {download_queue.qsize()} Einträge in Queue")
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Importieren: {e}")
    
    def import_from_clipboard(self):
        """Importiert URLs aus Zwischenablage"""
        try:
            clipboard_content = self.clipboard_get()
            lines = clipboard_content.split('\n')
            
            count = 0
            for line in lines:
                url = line.strip()
                if url and url.startswith('http'):
                    download_queue.put(url)
                    count += 1
            
            if count > 0:
                self.add_log(f"📋 {count} URLs aus Zwischenablage importiert")
                self.update_queue_display()
                self.status_label.configure(text=f"✅ {download_queue.qsize()} Einträge in Queue")
            else:
                messagebox.showinfo("Info", "Keine gültigen URLs in Zwischenablage gefunden")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Lesen der Zwischenablage: {e}")
    
    def clear_queue(self):
        """Leert die Queue"""
        if messagebox.askyesno("Bestätigung", "Queue wirklich leeren?"):
            while not download_queue.empty():
                try:
                    download_queue.get_nowait()
                except:
                    break
            
            self.add_log("🗑️ Queue geleert")
            self.update_queue_display()
            self.status_label.configure(text="Queue leer")
    
    def update_queue_display(self):
        """Aktualisiert Queue-Anzeige"""
        self.queue_textbox.configure(state="normal")
        self.queue_textbox.delete("1.0", "end")
        
        items = list(download_queue.queue)
        if items:
            for idx, url in enumerate(items, 1):
                self.queue_textbox.insert("end", f"{idx}. {url}\n")
        else:
            self.queue_textbox.insert("1.0", "Queue ist leer. Füge URLs hinzu!")
        
        self.queue_textbox.configure(state="disabled")
    
    def refresh_history(self):
        """Aktualisiert History-Anzeige"""
        self.history_textbox.configure(state="normal")
        self.history_textbox.delete("1.0", "end")
        
        history = load_history()
        
        if history:
            self.history_textbox.insert("1.0", "📊 Download-Verlauf (neueste zuerst):\n\n")
            for entry in reversed(history):
                timestamp = entry.get('timestamp', '')
                title = entry.get('title', '')
                url = entry.get('url', '')
                self.history_textbox.insert("end", f"⏰ {timestamp}\n📝 {title}\n🔗 {url}\n\n")
        else:
            self.history_textbox.insert("1.0", "Noch keine Downloads in der History.")
        
        self.history_textbox.configure(state="disabled")
    
    def clear_history(self):
        """Löscht History"""
        if messagebox.askyesno("Bestätigung", "History wirklich löschen?"):
            save_history([])
            self.refresh_history()
            self.add_log("🗑️ History geleert")
    
    def get_current_settings(self):
        """Holt aktuelle Einstellungen"""
        return {
            'download_folder': self.settings['download_folder'],
            'audio_format': self.audio_format_var.get().split()[0],
            'audio_quality': self.audio_quality_var.get().split()[0],
            'download_subtitles': self.download_subtitles_var.get(),
            'subtitle_language': self.subtitle_language_var.get(),
            'speed_limit': self.speed_limit_var.get(),
            'embed_thumbnail': self.embed_thumbnail_var.get(),
            'embed_metadata': self.embed_metadata_var.get(),
            'theme': self.settings['theme']
        }
    
    def save_settings_gui(self):
        """Speichert Einstellungen"""
        self.settings = self.get_current_settings()
        save_settings(self.settings)
        self.add_log("💾 Einstellungen gespeichert")
        messagebox.showinfo("Erfolg", "Einstellungen wurden gespeichert!")
    
    def update_ytdlp(self):
        """Aktualisiert yt-dlp"""
        self.status_label.configure(text="🔄 Aktualisiere yt-dlp...")
        Thread(target=self._update_ytdlp_thread, daemon=True).start()
    
    def _update_ytdlp_thread(self):
        """Thread für yt-dlp Update"""
        try:
            import subprocess
            result = subprocess.run(
                ['pip', 'install', '--upgrade', 'yt-dlp'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                self.add_log("✅ yt-dlp erfolgreich aktualisiert!")
                messagebox.showinfo("Erfolg", "yt-dlp wurde erfolgreich aktualisiert!")
                self.status_label.configure(text="✅ yt-dlp aktualisiert")
            else:
                self.add_log(f"❌ Update fehlgeschlagen: {result.stderr}")
                messagebox.showerror("Fehler", "yt-dlp konnte nicht aktualisiert werden!")
                self.status_label.configure(text="❌ Update fehlgeschlagen")
        except Exception as e:
            self.add_log(f"❌ Update fehlgeschlagen: {e}")
            messagebox.showerror("Fehler", f"Fehler: {e}")
            self.status_label.configure(text="❌ Update fehlgeschlagen")
    
    def update_system_status(self, nodejs_ok, ffmpeg_ok):
        """Aktualisiert System-Status-Labels"""
        if nodejs_ok:
            self.nodejs_status_label.configure(
                text="✅ Node.js: Verfügbar (JavaScript Runtime für yt-dlp)",
                text_color="#10B981"
            )
        else:
            self.nodejs_status_label.configure(
                text="⚠️ Node.js: NICHT gefunden - YouTube-Downloads könnten eingeschränkt sein",
                text_color="#EF4444"
            )
        
        if ffmpeg_ok:
            self.ffmpeg_status_label.configure(
                text="✅ FFmpeg: Verfügbar (Audio/Video-Konvertierung)",
                text_color="#10B981"
            )
        else:
            self.ffmpeg_status_label.configure(
                text="⚠️ FFmpeg: NICHT gefunden - Audio/Video-Konvertierung nicht möglich",
                text_color="#EF4444"
            )
    
    def add_log(self, message):
        """Fügt Log-Eintrag hinzu"""
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", f"{message}\n")
        self.log_textbox.see("end")
        self.log_textbox.configure(state="disabled")
    
    def process_queues(self):
        """Verarbeitet Message, Progress und Detailed Progress Queues"""
        # Messages
        while not message_queue.empty():
            msg = message_queue.get()
            self.add_log(msg)
        
        # Detaillierte Progress-Updates (neu!)
        while not detailed_progress_queue.empty():
            detail = detailed_progress_queue.get()
            status = detail.get('status', '')
            
            if status == 'downloading':
                # Zeige detaillierte Download-Info
                percent = detail.get('percent', '0%')
                speed = detail.get('speed', '?')
                size = detail.get('size', '?')
                eta = detail.get('eta', '?')
                title = detail.get('title', 'Unknown')
                
                # Kürze Titel falls nötig
                if len(title) > 50:
                    title = title[:47] + "..."
                
                detail_text = f"⬇️ {title}\n   📊 {percent} | 🚀 {speed} | 📦 {size} | ⏱️ ETA: {eta}"
                self.detail_progress_label.configure(text=detail_text, text_color="#3B82F6")
                
            elif status == 'processing':
                message = detail.get('message', 'Verarbeite...')
                self.detail_progress_label.configure(text=f"⚙️ {message}", text_color="#F59E0B")
                
            elif status == 'completed':
                title = detail.get('title', 'Unknown')
                if len(title) > 50:
                    title = title[:47] + "..."
                self.detail_progress_label.configure(text=f"✅ {title}", text_color="#10B981")
                
            elif status == 'error':
                title = detail.get('title', 'Unknown')
                error = detail.get('error', 'Unbekannter Fehler')
                if len(title) > 50:
                    title = title[:47] + "..."
                self.detail_progress_label.configure(text=f"❌ {title}\n   {error}", text_color="#EF4444")
        
        # Progress
        while not progress_queue.empty():
            data = progress_queue.get()
            
            if 'completed' in data and data['completed']:
                self.progress_bar.set(1.0)
                
                success = data.get('success', 0)
                errors = data.get('errors', 0)
                total = success + errors
                
                if errors == 0:
                    status_text = f"✅ Alle {success} Downloads erfolgreich abgeschlossen!"
                    self.progress_label.configure(text=status_text)
                    self.status_label.configure(text=status_text)
                else:
                    status_text = f"⚠️ {success} erfolgreich, {errors} Fehler von {total} Downloads"
                    self.progress_label.configure(text=status_text)
                    self.status_label.configure(text=status_text)
                
                self.detail_progress_label.configure(text="", text_color="#10B981")
                self.start_download_btn.configure(state="normal" if self.playlist_data else "disabled")
                self.load_playlist_btn.configure(state="normal")
                self.start_queue_btn.configure(state="normal")
                self.stop_download_btn.configure(state="disabled")
                self.refresh_history()
            else:
                current = data.get('current', 0)
                total = data.get('total', 1)
                song = data.get('song', '')
                percentage = (current / total)
                
                self.progress_bar.set(percentage)
                self.progress_label.configure(text=f"{current}/{total} Downloads")
        
        # Schedule next check
        self.after(100, self.process_queues)


def main():
    """Hauptfunktion"""
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    app = ModernDownloaderApp()
    app.mainloop()


if __name__ == '__main__':
    main()
