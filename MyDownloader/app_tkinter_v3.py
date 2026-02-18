import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
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
from PIL import Image, ImageTk
import requests
from io import BytesIO

# Globale Variablen
message_queue = queue.Queue()
progress_queue = queue.Queue()
download_running = False
download_queue = queue.Queue()

# Einstellungen laden/speichern
SETTINGS_FILE = "settings.json"

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

# Download-History
HISTORY_FILE = "download_history.json"

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
        # Limitiere auf letzte 100 Einträge
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

def download_ffmpeg_portable():
    """Lädt FFmpeg herunter und entpackt es im Projektordner"""
    log_message("🔄 Lade portable FFmpeg herunter...")
    
    ffmpeg_dir = os.path.join(os.getcwd(), "ffmpeg")
    bin_dir = os.path.join(ffmpeg_dir, "bin")
    
    # Prüfe ob schon vorhanden
    if os.path.exists(os.path.join(bin_dir, "ffmpeg.exe")):
        log_message("✅ Portable FFmpeg bereits vorhanden!")
        return bin_dir
    
    try:
        import urllib.request
        
        # Download URL für FFmpeg essentials build
        url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
        zip_path = "ffmpeg-temp.zip"
        
        log_message("📥 Downloading FFmpeg... (ca. 75 MB, kann etwas dauern)")
        urllib.request.urlretrieve(url, zip_path)
        
        log_message("📦 Entpacke FFmpeg...")
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
        
        log_message("✅ FFmpeg erfolgreich heruntergeladen!")
        return bin_dir
        
    except Exception as e:
        log_message(f"❌ FFmpeg-Download fehlgeschlagen: {e}")
        return None

def check_ffmpeg():
    """Prüft, ob FFmpeg verfügbar ist"""
    log_message("Prüfe FFmpeg...")
    
    # Prüfe zuerst im Projektordner (portable Version)
    local_ffmpeg = os.path.join(os.getcwd(), "ffmpeg", "bin")
    local_ffmpeg_exe = os.path.join(local_ffmpeg, "ffmpeg.exe")
    
    if os.path.exists(local_ffmpeg_exe):
        os.environ["PATH"] = local_ffmpeg + os.pathsep + os.environ.get("PATH", "")
        log_message("✅ FFmpeg gefunden (Portable Version)")
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
        winget_pattern = os.path.expanduser(r"~\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg*\ffmpeg-*\bin")
        possible_paths.extend(glob.glob(winget_pattern))
        
        for path_pattern in possible_paths:
            if os.path.exists(path_pattern):
                ffmpeg_test = os.path.join(path_pattern, "ffmpeg.exe")
                if os.path.exists(ffmpeg_test):
                    ffmpeg_path = ffmpeg_test
                    ffprobe_path = os.path.join(path_pattern, "ffprobe.exe")
                    os.environ["PATH"] = path_pattern + os.pathsep + os.environ["PATH"]
                    log_message(f"✅ FFmpeg gefunden: {path_pattern}")
                    return True
    
    if ffmpeg_path and ffprobe_path:
        log_message("✅ FFmpeg gefunden (System)")
        return True
    
    # FFmpeg nicht gefunden - lade portable Version herunter
    log_message("⚠️ FFmpeg nicht gefunden - starte Download...")
    bin_dir = download_ffmpeg_portable()
    if bin_dir:
        os.environ["PATH"] = bin_dir + os.pathsep + os.environ.get("PATH", "")
        return True
    
    return False

def update_ytdlp():
    """Aktualisiert yt-dlp"""
    try:
        log_message("🔄 Aktualisiere yt-dlp...")
        import subprocess
        result = subprocess.run(
            ['pip', 'install', '--upgrade', 'yt-dlp'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            log_message("✅ yt-dlp erfolgreich aktualisiert!")
            return True
        else:
            log_message(f"❌ Update fehlgeschlagen: {result.stderr}")
            return False
    except Exception as e:
        log_message(f"❌ Update fehlgeschlagen: {e}")
        return False

def parse_video_title(title):
    """Extrahiert Künstler und Titel aus YouTube-Videonamen"""
    original = title
    
    # Entferne häufige Zusätze
    patterns = [
        r'\s*\(official.*?\)',
        r'\s*\[official.*?\]',
        r'\s*\(HD\)',
        r'\s*\[HD\]',
        r'\s*\(4K\)',
        r'\s*\[4K\]',
        r'\s*\(Audio\)',
        r'\s*\[Audio\]',
        r'\s*\(Lyrics\)',
        r'\s*\[Lyrics\]',
        r'\s*\(Lyric Video\)',
        r'\s*\[Lyric Video\]',
        r'\s*\(Music Video\)',
        r'\s*\[Music Video\]',
        r'\s*ft\..*$',
        r'\s*feat\..*$',
        r'\s*\(prod\..*?\)',
        r'\s*\[prod\..*?\]',
    ]
    
    for pattern in patterns:
        title = re.sub(pattern, '', title, flags=re.IGNORECASE)
    
    title = title.strip()
    
    # Versuche "Künstler - Titel"-Format zu finden
    if ' - ' in title:
        parts = title.split(' - ', 1)
        return parts[0].strip(), parts[1].strip()
    
    return "Unknown Artist", original

def get_video_info(url):
    """Lädt Video-Informationen ohne Download"""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }
    
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
    log_message("Lade Playlist-Informationen...")
    
    # Extrahiere Playlist-ID aus URL
    parsed = urlparse(url)
    if "list=" in url:
        query_params = parse_qs(parsed.query)
        playlist_id = query_params.get("list", [None])[0]
        if playlist_id:
            url = f"https://www.youtube.com/playlist?list={playlist_id}"
    
    ydl_opts = {
        'extract_flat': True,
        'quiet': True,
        'yes_playlist': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            if 'entries' not in info:
                return None
            
            playlist_name = info.get('title', 'YouTube Playlist')
            songs = []
            
            for idx, entry in enumerate(info['entries'], 1):
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
            return {
                'name': playlist_name,
                'songs': songs,
                'url': url
            }
    except Exception as e:
        log_message(f"❌ Fehler beim Laden der Playlist: {e}")
        return None

def file_exists(save_dir, filename):
    """Prüft, ob eine Datei bereits existiert"""
    return os.path.exists(os.path.join(save_dir, filename))

def download_single(url, save_dir, settings, idx=1, total=1):
    """Lädt einzelnen Song/Video herunter"""
    
    # Update Progress
    progress_queue.put({
        'current': idx,
        'total': total,
        'song': url
    })
    
    log_message(f"🔍 [{idx}/{total}] Verarbeite: {url}")
    
    # Hole Video-Info
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'Unknown')
    except:
        title = "Unknown"
    
    # Erstelle Output-Template
    output_template = os.path.join(save_dir, "%(title)s.%(ext)s")
    
    # Basis-Optionen
    ydl_opts = {
        "outtmpl": output_template,
        "quiet": False,
        "no_warnings": False,
        "continuedl": True,
        "retries": 10,
    }
    
    # Audio-Format
    if settings.get('audio_format') and settings['audio_format'] != 'none':
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': settings['audio_format'],
            'preferredquality': settings.get('audio_quality', '0'),
        }]
        
        if settings.get('embed_thumbnail'):
            ydl_opts['postprocessors'].append({
                'key': 'EmbedThumbnail',
            })
            ydl_opts['writethumbnail'] = True
        
        if settings.get('embed_metadata'):
            ydl_opts['postprocessors'].append({
                'key': 'FFmpegMetadata',
            })
    else:
        # Video
        ydl_opts['format'] = 'bestvideo+bestaudio/best'
    
    # Untertitel
    if settings.get('download_subtitles'):
        ydl_opts['writesubtitles'] = True
        ydl_opts['subtitleslangs'] = settings.get('subtitle_language', 'de,en').split(',')
        ydl_opts['subtitlesformat'] = 'srt'
    
    # Geschwindigkeitslimit
    if settings.get('speed_limit'):
        ydl_opts['ratelimit'] = int(settings['speed_limit']) * 1024 * 1024  # MB/s zu Bytes/s
    
    try:
        log_message(f"📥 [{idx}/{total}] Download: {title}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        log_message(f"✅ [{idx}/{total}] Erfolgreich: {title}")
        
        # Zur History hinzufügen
        add_to_history(url, title)
        
        return True
    except Exception as e:
        log_message(f"❌ [{idx}/{total}] Fehler: {title} - {e}")
        return False

def search_and_download(song, save_dir, settings, idx, total):
    """Sucht und lädt einen Song herunter"""
    artist = clean(song["artist"])
    title = clean(song["title"])
    original_url = song.get("original_url", None)
    original_title = song.get("original_title", "")
    
    # Update Progress
    progress_queue.put({
        'current': idx,
        'total': total,
        'song': f"{artist} - {title}"
    })
    
    # Dateiname im Format: "Künstler - Titel"
    filename = f"{artist} - {title}.{settings.get('audio_format', 'mp3')}"
    
    # Prüfe, ob der Song bereits existiert
    if file_exists(save_dir, filename):
        log_message(f"⏭️ [{idx}/{total}] Überspringe: {artist} - {title} (bereits vorhanden)")
        return "skipped"
    
    # Nutze single download mit original URL
    if original_url:
        return download_single(original_url, save_dir, settings, idx, total)
    
    return False

def download_playlist_thread(playlist_data, settings):
    """Thread-Funktion für Playlist-Downloads"""
    global download_running
    download_running = True
    
    playlist_name = playlist_data['name']
    songs = playlist_data['songs']
    
    # Erstelle Ausgabeverzeichnis
    base_dir = os.path.join(settings['download_folder'], clean(playlist_name))
    os.makedirs(base_dir, exist_ok=True)
    
    log_message(f"\n{'='*60}")
    log_message(f"Download startet: {playlist_name}")
    log_message(f"Anzahl Songs: {len(songs)}")
    log_message(f"Speicherort: {base_dir}")
    log_message(f"{'='*60}\n")
    
    success_count = 0
    skipped_count = 0
    error_count = 0
    
    for idx, song in enumerate(songs, 1):
        if not download_running:
            log_message("\n⚠️ Download abgebrochen!")
            break
        
        result = search_and_download(song, base_dir, settings, idx, len(songs))
        
        if result == "skipped":
            skipped_count += 1
        elif result:
            success_count += 1
        else:
            error_count += 1
    
    log_message(f"\n{'='*60}")
    log_message(f"Download abgeschlossen!")
    log_message(f"✅ Erfolgreich: {success_count}")
    log_message(f"⏭️ Übersprungen: {skipped_count}")
    log_message(f"❌ Fehler: {error_count}")
    log_message(f"📁 Speicherort: {base_dir}")
    log_message(f"{'='*60}\n")
    
    # Zur History hinzufügen
    add_to_history(playlist_data.get('url', ''), playlist_name)
    
    download_running = False
    progress_queue.put({'completed': True})

def download_queue_thread(settings):
    """Thread-Funktion für Queue-Downloads"""
    global download_running
    download_running = True
    
    items = []
    while not download_queue.empty():
        items.append(download_queue.get())
    
    if not items:
        log_message("⚠️ Queue ist leer!")
        download_running = False
        progress_queue.put({'completed': True})
        return
    
    base_dir = settings['download_folder']
    os.makedirs(base_dir, exist_ok=True)
    
    log_message(f"\n{'='*60}")
    log_message(f"Queue-Download startet")
    log_message(f"Anzahl Items: {len(items)}")
    log_message(f"Speicherort: {base_dir}")
    log_message(f"{'='*60}\n")
    
    success_count = 0
    error_count = 0
    
    for idx, url in enumerate(items, 1):
        if not download_running:
            log_message("\n⚠️ Download abgebrochen!")
            break
        
        result = download_single(url, base_dir, settings, idx, len(items))
        
        if result:
            success_count += 1
        else:
            error_count += 1
    
    log_message(f"\n{'='*60}")
    log_message(f"Queue-Download abgeschlossen!")
    log_message(f"✅ Erfolgreich: {success_count}")
    log_message(f"❌ Fehler: {error_count}")
    log_message(f"📁 Speicherort: {base_dir}")
    log_message(f"{'='*60}\n")
    
    download_running = False
    progress_queue.put({'completed': True})

def log_message(msg):
    """Fügt Nachricht zur Queue hinzu"""
    message_queue.put(msg)

# GUI-Klasse
class PlaylistDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎵 Ultimate Music & Video Downloader")
        self.root.geometry("1100x800")
        self.root.resizable(True, True)
        
        # Einstellungen laden
        self.settings = load_settings()
        
        # Theme konfigurieren
        self.setup_theme()
        
        # Erstelle Notebook (Tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tabs erstellen
        self.create_download_tab()
        self.create_queue_tab()
        self.create_history_tab()
        self.create_settings_tab()
        self.create_about_tab()
        
        # Status Bar
        self.create_status_bar()
        
        # Daten
        self.playlist_data = None
        self.preview_info = None
        
        # Start FFmpeg Check
        self.check_ffmpeg_startup()
        
        # Start Queue Processing
        self.process_queues()
    
    def setup_theme(self):
        """Konfiguriert das Theme"""
        self.style = ttk.Style()
        
        # Verfügbare Themes anzeigen
        # print("Verfügbare Themes:", self.style.theme_names())
        
        # Nutze 'vista' oder 'winnative' für Windows-Look
        if 'vista' in self.style.theme_names():
            self.style.theme_use('vista')
        elif 'winnative' in self.style.theme_names():
            self.style.theme_use('winnative')
        else:
            self.style.theme_use('clam')
        
        # Farben
        if self.settings.get('theme') == 'dark':
            self.bg_color = '#1e1e1e'
            self.fg_color = '#ffffff'
            self.accent_color = '#1db954'
            self.surface_color = '#282828'
        else:
            self.bg_color = '#f0f0f0'
            self.fg_color = '#000000'
            self.accent_color = '#0078d4'
            self.surface_color = '#ffffff'
        
        self.root.configure(bg=self.bg_color)
    
    def create_download_tab(self):
        """Erstellt den Haupt-Download-Tab"""
        tab = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(tab, text="📥 Download")
        
        # Header
        header_frame = tk.Frame(tab, bg=self.surface_color, height=60)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="🎵 Music & Video Downloader",
            font=("Segoe UI", 16, "bold"),
            bg=self.surface_color,
            fg=self.accent_color
        )
        title_label.pack(pady=15)
        
        # Main Content
        main_frame = tk.Frame(tab, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # URL Input Frame
        input_frame = tk.LabelFrame(
            main_frame,
            text="🔗 Video/Playlist URL",
            font=("Segoe UI", 10, "bold"),
            bg=self.surface_color,
            fg=self.fg_color,
            padx=10,
            pady=10
        )
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        url_input_frame = tk.Frame(input_frame, bg=self.surface_color)
        url_input_frame.pack(fill=tk.X)
        
        self.url_var = tk.StringVar()
        url_entry = tk.Entry(
            url_input_frame,
            textvariable=self.url_var,
            font=("Segoe UI", 10),
            bg='white',
            fg='black',
            relief=tk.SOLID,
            bd=1
        )
        url_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        preview_btn = tk.Button(
            url_input_frame,
            text="👁️ Vorschau",
            command=self.show_preview,
            font=("Segoe UI", 9),
            bg=self.accent_color,
            fg='white',
            relief=tk.FLAT,
            padx=10,
            cursor='hand2'
        )
        preview_btn.pack(side=tk.LEFT)
        
        # Buttons Frame
        button_frame = tk.Frame(input_frame, bg=self.surface_color)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.load_playlist_btn = tk.Button(
            button_frame,
            text="📋 Playlist laden",
            command=self.load_playlist,
            font=("Segoe UI", 9, "bold"),
            bg=self.accent_color,
            fg='white',
            relief=tk.FLAT,
            padx=15,
            pady=8,
            cursor='hand2'
        )
        self.load_playlist_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.download_single_btn = tk.Button(
            button_frame,
            text="⬇️ Einzeln Download",
            command=self.download_single_video,
            font=("Segoe UI", 9, "bold"),
            bg='#4CAF50',
            fg='white',
            relief=tk.FLAT,
            padx=15,
            pady=8,
            cursor='hand2'
        )
        self.download_single_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.add_to_queue_btn = tk.Button(
            button_frame,
            text="➕ Zur Queue",
            command=self.add_to_queue,
            font=("Segoe UI", 9, "bold"),
            bg='#FF9800',
            fg='white',
            relief=tk.FLAT,
            padx=15,
            pady=8,
            cursor='hand2'
        )
        self.add_to_queue_btn.pack(side=tk.LEFT)
        
        # Preview/Playlist Info Frame
        self.info_frame = tk.LabelFrame(
            main_frame,
            text="ℹ️ Informationen",
            font=("Segoe UI", 10, "bold"),
            bg=self.surface_color,
            fg=self.fg_color,
            padx=10,
            pady=10
        )
        self.info_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.info_text = scrolledtext.ScrolledText(
            self.info_frame,
            font=("Segoe UI", 9),
            bg='white',
            fg='black',
            relief=tk.SOLID,
            bd=1,
            wrap=tk.WORD,
            height=8,
            state=tk.DISABLED
        )
        self.info_text.pack(fill=tk.BOTH, expand=True)
        
        # Download Control Frame
        control_frame = tk.LabelFrame(
            main_frame,
            text="🎛️ Download Steuerung",
            font=("Segoe UI", 10, "bold"),
            bg=self.surface_color,
            fg=self.fg_color,
            padx=10,
            pady=10
        )
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Download Folder Selection
        folder_frame = tk.Frame(control_frame, bg=self.surface_color)
        folder_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            folder_frame,
            text="📁 Download-Ordner:",
            font=("Segoe UI", 9),
            bg=self.surface_color,
            fg=self.fg_color
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.folder_var = tk.StringVar(value=self.settings['download_folder'])
        folder_entry = tk.Entry(
            folder_frame,
            textvariable=self.folder_var,
            font=("Segoe UI", 9),
            bg='white',
            fg='black',
            relief=tk.SOLID,
            bd=1,
            state='readonly'
        )
        folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        folder_btn = tk.Button(
            folder_frame,
            text="🗂️ Ändern",
            command=self.select_download_folder,
            font=("Segoe UI", 9),
            bg=self.accent_color,
            fg='white',
            relief=tk.FLAT,
            padx=10,
            cursor='hand2'
        )
        folder_btn.pack(side=tk.LEFT)
        
        # Buttons
        btn_frame = tk.Frame(control_frame, bg=self.surface_color)
        btn_frame.pack(fill=tk.X)
        
        self.start_download_btn = tk.Button(
            btn_frame,
            text="▶️ Playlist Download starten",
            command=self.start_playlist_download,
            font=("Segoe UI", 10, "bold"),
            bg='#4CAF50',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor='hand2',
            state=tk.DISABLED
        )
        self.start_download_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_download_btn = tk.Button(
            btn_frame,
            text="⏹️ Abbrechen",
            command=self.stop_download,
            font=("Segoe UI", 10, "bold"),
            bg='#e74c3c',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor='hand2',
            state=tk.DISABLED
        )
        self.stop_download_btn.pack(side=tk.LEFT)
        
        # Progress Frame
        progress_frame = tk.LabelFrame(
            main_frame,
            text="📊 Fortschritt",
            font=("Segoe UI", 10, "bold"),
            bg=self.surface_color,
            fg=self.fg_color,
            padx=10,
            pady=10
        )
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.progress_var = tk.StringVar(value="Bereit")
        progress_label = tk.Label(
            progress_frame,
            textvariable=self.progress_var,
            font=("Segoe UI", 9),
            bg=self.surface_color,
            fg=self.fg_color
        )
        progress_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Windows-Style Progressbar
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode='determinate',
            length=400
        )
        self.progress_bar.pack(fill=tk.X)
        
        # Log Frame
        log_frame = tk.LabelFrame(
            main_frame,
            text="📝 Aktivität",
            font=("Segoe UI", 10, "bold"),
            bg=self.surface_color,
            fg=self.fg_color,
            padx=10,
            pady=10
        )
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            font=("Consolas", 8),
            bg='#0d0d0d' if self.settings.get('theme') == 'dark' else 'white',
            fg='#00ff00' if self.settings.get('theme') == 'dark' else 'black',
            relief=tk.SOLID,
            bd=1,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
    
    def create_queue_tab(self):
        """Erstellt den Queue-Tab"""
        tab = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(tab, text="📑 Queue")
        
        main_frame = tk.Frame(tab, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Controls
        control_frame = tk.LabelFrame(
            main_frame,
            text="🎛️ Queue-Steuerung",
            font=("Segoe UI", 10, "bold"),
            bg=self.surface_color,
            fg=self.fg_color,
            padx=10,
            pady=10
        )
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        btn_frame = tk.Frame(control_frame, bg=self.surface_color)
        btn_frame.pack(fill=tk.X)
        
        import_file_btn = tk.Button(
            btn_frame,
            text="📄 Aus Datei importieren",
            command=self.import_from_file,
            font=("Segoe UI", 9, "bold"),
            bg=self.accent_color,
            fg='white',
            relief=tk.FLAT,
            padx=15,
            pady=8,
            cursor='hand2'
        )
        import_file_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        import_clipboard_btn = tk.Button(
            btn_frame,
            text="📋 Aus Zwischenablage",
            command=self.import_from_clipboard,
            font=("Segoe UI", 9, "bold"),
            bg=self.accent_color,
            fg='white',
            relief=tk.FLAT,
            padx=15,
            pady=8,
            cursor='hand2'
        )
        import_clipboard_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        clear_queue_btn = tk.Button(
            btn_frame,
            text="🗑️ Queue leeren",
            command=self.clear_queue,
            font=("Segoe UI", 9, "bold"),
            bg='#e74c3c',
            fg='white',
            relief=tk.FLAT,
            padx=15,
            pady=8,
            cursor='hand2'
        )
        clear_queue_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.start_queue_btn = tk.Button(
            btn_frame,
            text="▶️ Queue starten",
            command=self.start_queue_download,
            font=("Segoe UI", 9, "bold"),
            bg='#4CAF50',
            fg='white',
            relief=tk.FLAT,
            padx=15,
            pady=8,
            cursor='hand2'
        )
        self.start_queue_btn.pack(side=tk.LEFT)
        
        # Queue List
        list_frame = tk.LabelFrame(
            main_frame,
            text="📋 Queue-Einträge",
            font=("Segoe UI", 10, "bold"),
            bg=self.surface_color,
            fg=self.fg_color,
            padx=10,
            pady=10
        )
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar für Listbox
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.queue_listbox = tk.Listbox(
            list_frame,
            font=("Segoe UI", 9),
            bg='white',
            fg='black',
            relief=tk.SOLID,
            bd=1,
            yscrollcommand=scrollbar.set
        )
        self.queue_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.queue_listbox.yview)
        
        # Context Menu
        self.queue_menu = tk.Menu(self.queue_listbox, tearoff=0)
        self.queue_menu.add_command(label="❌ Entfernen", command=self.remove_from_queue)
        
        self.queue_listbox.bind("<Button-3>", self.show_queue_menu)
    
    def create_history_tab(self):
        """Erstellt den History-Tab"""
        tab = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(tab, text="📜 History")
        
        main_frame = tk.Frame(tab, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Controls
        control_frame = tk.Frame(main_frame, bg=self.surface_color)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        refresh_btn = tk.Button(
            control_frame,
            text="🔄 Aktualisieren",
            command=self.refresh_history,
            font=("Segoe UI", 9, "bold"),
            bg=self.accent_color,
            fg='white',
            relief=tk.FLAT,
            padx=15,
            pady=8,
            cursor='hand2'
        )
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        clear_history_btn = tk.Button(
            control_frame,
            text="🗑️ History löschen",
            command=self.clear_history,
            font=("Segoe UI", 9, "bold"),
            bg='#e74c3c',
            fg='white',
            relief=tk.FLAT,
            padx=15,
            pady=8,
            cursor='hand2'
        )
        clear_history_btn.pack(side=tk.LEFT, padx=5)
        
        # History Table
        list_frame = tk.LabelFrame(
            main_frame,
            text="📊 Download-Verlauf",
            font=("Segoe UI", 10, "bold"),
            bg=self.surface_color,
            fg=self.fg_color,
            padx=10,
            pady=10
        )
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview für bessere Darstellung
        columns = ('Datum/Zeit', 'Titel', 'URL')
        self.history_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        self.history_tree.heading('Datum/Zeit', text='Datum/Zeit')
        self.history_tree.heading('Titel', text='Titel')
        self.history_tree.heading('URL', text='URL')
        
        self.history_tree.column('Datum/Zeit', width=150)
        self.history_tree.column('Titel', width=300)
        self.history_tree.column('URL', width=400)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscroll=scrollbar.set)
        
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load History
        self.refresh_history()
    
    def create_settings_tab(self):
        """Erstellt den Einstellungs-Tab"""
        tab = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(tab, text="⚙️ Einstellungen")
        
        # Scrollable Frame
        canvas = tk.Canvas(tab, bg=self.bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.bg_color)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")
        
        # Audio-Einstellungen
        audio_frame = tk.LabelFrame(
            scrollable_frame,
            text="🎵 Audio-Einstellungen",
            font=("Segoe UI", 10, "bold"),
            bg=self.surface_color,
            fg=self.fg_color,
            padx=15,
            pady=15
        )
        audio_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Audio Format
        format_frame = tk.Frame(audio_frame, bg=self.surface_color)
        format_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            format_frame,
            text="Format:",
            font=("Segoe UI", 9),
            bg=self.surface_color,
            fg=self.fg_color,
            width=20,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        self.audio_format_var = tk.StringVar(value=self.settings.get('audio_format', 'mp3'))
        formats = ['mp3', 'm4a', 'opus', 'flac', 'wav', 'none (Video)']
        format_combo = ttk.Combobox(
            format_frame,
            textvariable=self.audio_format_var,
            values=formats,
            state='readonly',
            width=15
        )
        format_combo.pack(side=tk.LEFT)
        
        # Audio Quality
        quality_frame = tk.Frame(audio_frame, bg=self.surface_color)
        quality_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            quality_frame,
            text="Qualität:",
            font=("Segoe UI", 9),
            bg=self.surface_color,
            fg=self.fg_color,
            width=20,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        self.audio_quality_var = tk.StringVar(value=self.settings.get('audio_quality', '0'))
        qualities = ['0 (Beste)', '2', '5', '9 (Kleinste)']
        quality_combo = ttk.Combobox(
            quality_frame,
            textvariable=self.audio_quality_var,
            values=qualities,
            state='readonly',
            width=15
        )
        quality_combo.pack(side=tk.LEFT)
        
        # Embed Options
        self.embed_thumbnail_var = tk.BooleanVar(value=self.settings.get('embed_thumbnail', True))
        embed_thumb_check = tk.Checkbutton(
            audio_frame,
            text="🖼️ Thumbnail einbetten",
            variable=self.embed_thumbnail_var,
            font=("Segoe UI", 9),
            bg=self.surface_color,
            fg=self.fg_color,
            selectcolor=self.surface_color,
            activebackground=self.surface_color
        )
        embed_thumb_check.pack(anchor='w', pady=2)
        
        self.embed_metadata_var = tk.BooleanVar(value=self.settings.get('embed_metadata', True))
        embed_meta_check = tk.Checkbutton(
            audio_frame,
            text="📝 Metadaten einbetten",
            variable=self.embed_metadata_var,
            font=("Segoe UI", 9),
            bg=self.surface_color,
            fg=self.fg_color,
            selectcolor=self.surface_color,
            activebackground=self.surface_color
        )
        embed_meta_check.pack(anchor='w', pady=2)
        
        # Untertitel-Einstellungen
        subtitle_frame = tk.LabelFrame(
            scrollable_frame,
            text="💬 Untertitel-Einstellungen",
            font=("Segoe UI", 10, "bold"),
            bg=self.surface_color,
            fg=self.fg_color,
            padx=15,
            pady=15
        )
        subtitle_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.download_subtitles_var = tk.BooleanVar(value=self.settings.get('download_subtitles', False))
        subtitle_check = tk.Checkbutton(
            subtitle_frame,
            text="📥 Untertitel herunterladen",
            variable=self.download_subtitles_var,
            font=("Segoe UI", 9),
            bg=self.surface_color,
            fg=self.fg_color,
            selectcolor=self.surface_color,
            activebackground=self.surface_color
        )
        subtitle_check.pack(anchor='w', pady=5)
        
        lang_frame = tk.Frame(subtitle_frame, bg=self.surface_color)
        lang_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            lang_frame,
            text="Sprachen (z.B. de,en):",
            font=("Segoe UI", 9),
            bg=self.surface_color,
            fg=self.fg_color,
            width=20,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        self.subtitle_language_var = tk.StringVar(value=self.settings.get('subtitle_language', 'de,en'))
        lang_entry = tk.Entry(
            lang_frame,
            textvariable=self.subtitle_language_var,
            font=("Segoe UI", 9),
            bg='white',
            fg='black',
            width=15
        )
        lang_entry.pack(side=tk.LEFT)
        
        # Download-Einstellungen
        download_frame = tk.LabelFrame(
            scrollable_frame,
            text="⚡ Download-Einstellungen",
            font=("Segoe UI", 10, "bold"),
            bg=self.surface_color,
            fg=self.fg_color,
            padx=15,
            pady=15
        )
        download_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Speed Limit
        speed_frame = tk.Frame(download_frame, bg=self.surface_color)
        speed_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            speed_frame,
            text="Geschwindigkeitslimit (MB/s):",
            font=("Segoe UI", 9),
            bg=self.surface_color,
            fg=self.fg_color,
            width=25,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        self.speed_limit_var = tk.StringVar(value=self.settings.get('speed_limit', ''))
        speed_entry = tk.Entry(
            speed_frame,
            textvariable=self.speed_limit_var,
            font=("Segoe UI", 9),
            bg='white',
            fg='black',
            width=10
        )
        speed_entry.pack(side=tk.LEFT)
        
        tk.Label(
            speed_frame,
            text="(leer = unbegrenzt)",
            font=("Segoe UI", 8, "italic"),
            bg=self.surface_color,
            fg=self.fg_color
        ).pack(side=tk.LEFT, padx=5)
        
        # Aussehen
        appearance_frame = tk.LabelFrame(
            scrollable_frame,
            text="🎨 Aussehen",
            font=("Segoe UI", 10, "bold"),
            bg=self.surface_color,
            fg=self.fg_color,
            padx=15,
            pady=15
        )
        appearance_frame.pack(fill=tk.X, pady=(0, 10))
        
        theme_frame = tk.Frame(appearance_frame, bg=self.surface_color)
        theme_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            theme_frame,
            text="Theme:",
            font=("Segoe UI", 9),
            bg=self.surface_color,
            fg=self.fg_color,
            width=20,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        self.theme_var = tk.StringVar(value=self.settings.get('theme', 'dark'))
        themes = ['dark', 'light']
        theme_combo = ttk.Combobox(
            theme_frame,
            textvariable=self.theme_var,
            values=themes,
            state='readonly',
            width=15
        )
        theme_combo.pack(side=tk.LEFT)
        
        tk.Label(
            theme_frame,
            text="(Neustart erforderlich)",
            font=("Segoe UI", 8, "italic"),
            bg=self.surface_color,
            fg=self.fg_color
        ).pack(side=tk.LEFT, padx=5)
        
        # Buttons
        button_frame = tk.Frame(scrollable_frame, bg=self.bg_color)
        button_frame.pack(fill=tk.X, pady=20)
        
        save_btn = tk.Button(
            button_frame,
            text="💾 Einstellungen speichern",
            command=self.save_settings_gui,
            font=("Segoe UI", 10, "bold"),
            bg='#4CAF50',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor='hand2'
        )
        save_btn.pack(side=tk.LEFT, padx=5)
        
        update_btn = tk.Button(
            button_frame,
            text="🔄 yt-dlp aktualisieren",
            command=self.update_ytdlp_gui,
            font=("Segoe UI", 10, "bold"),
            bg=self.accent_color,
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor='hand2'
        )
        update_btn.pack(side=tk.LEFT, padx=5)
    
    def create_about_tab(self):
        """Erstellt den About-Tab"""
        tab = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(tab, text="ℹ️ Info")
        
        main_frame = tk.Frame(tab, bg=self.surface_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="🎵 Ultimate Music & Video Downloader",
            font=("Segoe UI", 18, "bold"),
            bg=self.surface_color,
            fg=self.accent_color
        )
        title_label.pack(pady=(20, 10))
        
        # Version
        version_label = tk.Label(
            main_frame,
            text="Version 3.0",
            font=("Segoe UI", 12),
            bg=self.surface_color,
            fg=self.fg_color
        )
        version_label.pack(pady=5)
        
        # Separator
        ttk.Separator(main_frame, orient='horizontal').pack(fill=tk.X, pady=20)
        
        # Features
        features_label = tk.Label(
            main_frame,
            text="✨ Features:",
            font=("Segoe UI", 12, "bold"),
            bg=self.surface_color,
            fg=self.fg_color
        )
        features_label.pack(anchor='w', pady=(10, 5))
        
        features = [
            "📥 Download einzelner Videos/Songs",
            "📋 Download kompletter Playlists",
            "📑 Queue-System für Batch-Downloads",
            "👁️ Vorschau vor dem Download",
            "🎵 Unterstützung für MP3, M4A, FLAC, OPUS, WAV",
            "💬 Untertitel-Download",
            "📊 Download-History",
            "⚙️ Umfangreiche Einstellungen",
            "🎨 Dark/Light Theme",
            "⚡ Geschwindigkeitslimits",
            "📁 Frei wählbarer Download-Ordner"
        ]
        
        for feature in features:
            feature_label = tk.Label(
                main_frame,
                text=feature,
                font=("Segoe UI", 10),
                bg=self.surface_color,
                fg=self.fg_color
            )
            feature_label.pack(anchor='w', padx=20, pady=2)
        
        # Separator
        ttk.Separator(main_frame, orient='horizontal').pack(fill=tk.X, pady=20)
        
        # Credits
        credits_label = tk.Label(
            main_frame,
            text="Made with ❤️ using Python, yt-dlp & FFmpeg",
            font=("Segoe UI", 10, "italic"),
            bg=self.surface_color,
            fg=self.fg_color
        )
        credits_label.pack(pady=10)
    
    def create_status_bar(self):
        """Erstellt die Status-Bar"""
        status_frame = tk.Frame(self.root, bg=self.surface_color, height=25)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)
        
        self.status_var = tk.StringVar(value="Bereit")
        status_label = tk.Label(
            status_frame,
            textvariable=self.status_var,
            font=("Segoe UI", 8),
            bg=self.surface_color,
            fg=self.fg_color,
            anchor=tk.W
        )
        status_label.pack(fill=tk.X, padx=10, pady=3)
    
    # Funktionen
    def select_download_folder(self):
        """Ordner-Auswahl Dialog"""
        folder = filedialog.askdirectory(
            title="Download-Ordner auswählen",
            initialdir=self.folder_var.get()
        )
        
        if folder:
            self.folder_var.set(folder)
            self.settings['download_folder'] = folder
            save_settings(self.settings)
            self.add_log(f"📁 Download-Ordner geändert: {folder}")
            self.status_var.set(f"Download-Ordner: {folder}")
    
    def show_preview(self):
        """Zeigt Vorschau des Videos"""
        url = self.url_var.get().strip()
        
        if not url:
            messagebox.showwarning("Fehler", "Bitte eine URL eingeben!")
            return
        
        self.status_var.set("⏳ Lade Vorschau...")
        thread = Thread(target=self._load_preview_thread, args=(url,), daemon=True)
        thread.start()
    
    def _load_preview_thread(self, url):
        """Thread für Vorschau"""
        info = get_video_info(url)
        
        if info:
            self.preview_info = info
            
            # Update Info Text
            info_text = f"""
📹 Titel: {info['title']}
👤 Uploader: {info['uploader']}
⏱️ Dauer: {info['duration'] // 60}:{info['duration'] % 60:02d}
👁️ Views: {info.get('view_count', 0):,}
🔗 URL: {info['url']}
            """
            
            self.info_text.config(state=tk.NORMAL)
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(tk.END, info_text.strip())
            self.info_text.config(state=tk.DISABLED)
            
            self.root.after(0, lambda: self.status_var.set("✅ Vorschau geladen"))
        else:
            self.root.after(0, lambda: messagebox.showerror(
                "Fehler", "Vorschau konnte nicht geladen werden!"
            ))
            self.root.after(0, lambda: self.status_var.set("❌ Fehler beim Laden"))
    
    def load_playlist(self):
        """Lädt Playlist"""
        url = self.url_var.get().strip()
        
        if not url:
            messagebox.showwarning("Fehler", "Bitte eine URL eingeben!")
            return
        
        self.load_playlist_btn.config(state=tk.DISABLED)
        self.status_var.set("⏳ Lade Playlist...")
        
        thread = Thread(target=self._load_playlist_thread, args=(url,), daemon=True)
        thread.start()
    
    def _load_playlist_thread(self, url):
        """Thread für Playlist-Laden"""
        self.playlist_data = get_youtube_playlist(url)
        
        if self.playlist_data:
            # Update Info
            info_text = f"""
📋 Playlist: {self.playlist_data['name']}
🎵 Anzahl Songs: {len(self.playlist_data['songs'])}
🔗 URL: {self.playlist_data.get('url', '')}

Songs:
"""
            for idx, song in enumerate(self.playlist_data['songs'][:10], 1):
                info_text += f"{idx}. {song['artist']} - {song['title']}\n"
            
            if len(self.playlist_data['songs']) > 10:
                info_text += f"... und {len(self.playlist_data['songs']) - 10} weitere"
            
            self.info_text.config(state=tk.NORMAL)
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(tk.END, info_text.strip())
            self.info_text.config(state=tk.DISABLED)
            
            self.root.after(0, lambda: self.start_download_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.status_var.set(
                f"✅ Playlist geladen: {self.playlist_data['name']} ({len(self.playlist_data['songs'])} Songs)"
            ))
        else:
            self.root.after(0, lambda: messagebox.showerror(
                "Fehler", "Playlist konnte nicht geladen werden!"
            ))
            self.root.after(0, lambda: self.status_var.set("❌ Fehler beim Laden"))
        
        self.root.after(0, lambda: self.load_playlist_btn.config(state=tk.NORMAL))
    
    def download_single_video(self):
        """Lädt einzelnes Video herunter"""
        url = self.url_var.get().strip()
        
        if not url:
            messagebox.showwarning("Fehler", "Bitte eine URL eingeben!")
            return
        
        self.download_single_btn.config(state=tk.DISABLED)
        self.stop_download_btn.config(state=tk.NORMAL)
        self.status_var.set("▶️ Download läuft...")
        
        # Get current settings from GUI
        current_settings = self.get_current_settings()
        
        thread = Thread(target=self._download_single_thread, args=(url, current_settings), daemon=True)
        thread.start()
    
    def _download_single_thread(self, url, settings):
        """Thread für Einzel-Download"""
        global download_running
        download_running = True
        
        download_single(url, settings['download_folder'], settings, 1, 1)
        
        download_running = False
        progress_queue.put({'completed': True})
        
        self.root.after(0, lambda: self.download_single_btn.config(state=tk.NORMAL))
        self.root.after(0, lambda: self.stop_download_btn.config(state=tk.DISABLED))
    
    def add_to_queue(self):
        """Fügt URL zur Queue hinzu"""
        url = self.url_var.get().strip()
        
        if not url:
            messagebox.showwarning("Fehler", "Bitte eine URL eingeben!")
            return
        
        download_queue.put(url)
        self.queue_listbox.insert(tk.END, url)
        self.add_log(f"➕ Zur Queue hinzugefügt: {url}")
        self.status_var.set(f"✅ {self.queue_listbox.size()} Einträge in Queue")
        self.url_var.set("")  # Clear input
    
    def start_playlist_download(self):
        """Startet Playlist-Download"""
        if not self.playlist_data:
            messagebox.showwarning("Fehler", "Bitte zuerst eine Playlist laden!")
            return
        
        self.start_download_btn.config(state=tk.DISABLED)
        self.load_playlist_btn.config(state=tk.DISABLED)
        self.stop_download_btn.config(state=tk.NORMAL)
        self.progress_bar['value'] = 0
        self.status_var.set("▶️ Playlist-Download läuft...")
        
        # Get current settings from GUI
        current_settings = self.get_current_settings()
        
        thread = Thread(target=download_playlist_thread, args=(self.playlist_data, current_settings), daemon=True)
        thread.start()
    
    def start_queue_download(self):
        """Startet Queue-Download"""
        if self.queue_listbox.size() == 0:
            messagebox.showwarning("Fehler", "Queue ist leer!")
            return
        
        self.start_queue_btn.config(state=tk.DISABLED)
        self.stop_download_btn.config(state=tk.NORMAL)
        self.status_var.set("▶️ Queue-Download läuft...")
        
        # Get current settings from GUI
        current_settings = self.get_current_settings()
        
        thread = Thread(target=download_queue_thread, args=(current_settings,), daemon=True)
        thread.start()
    
    def stop_download(self):
        """Stoppt Download"""
        global download_running
        download_running = False
        self.stop_download_btn.config(state=tk.DISABLED)
        self.status_var.set("⏹️ Download wird abgebrochen...")
    
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
                        self.queue_listbox.insert(tk.END, url)
                        count += 1
                
                self.add_log(f"📄 {count} URLs aus Datei importiert")
                self.status_var.set(f"✅ {self.queue_listbox.size()} Einträge in Queue")
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Importieren: {e}")
    
    def import_from_clipboard(self):
        """Importiert URLs aus Zwischenablage"""
        try:
            clipboard_content = self.root.clipboard_get()
            lines = clipboard_content.split('\n')
            
            count = 0
            for line in lines:
                url = line.strip()
                if url and url.startswith('http'):
                    download_queue.put(url)
                    self.queue_listbox.insert(tk.END, url)
                    count += 1
            
            if count > 0:
                self.add_log(f"📋 {count} URLs aus Zwischenablage importiert")
                self.status_var.set(f"✅ {self.queue_listbox.size()} Einträge in Queue")
            else:
                messagebox.showinfo("Info", "Keine gültigen URLs in Zwischenablage gefunden")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Lesen der Zwischenablage: {e}")
    
    def clear_queue(self):
        """Leert die Queue"""
        if messagebox.askyesno("Bestätigung", "Queue wirklich leeren?"):
            # Clear queue
            while not download_queue.empty():
                try:
                    download_queue.get_nowait()
                except:
                    break
            
            self.queue_listbox.delete(0, tk.END)
            self.add_log("🗑️ Queue geleert")
            self.status_var.set("Queue leer")
    
    def remove_from_queue(self):
        """Entfernt ausgewählten Eintrag aus Queue"""
        selection = self.queue_listbox.curselection()
        if selection:
            self.queue_listbox.delete(selection)
            self.add_log("❌ Eintrag aus Queue entfernt")
    
    def show_queue_menu(self, event):
        """Zeigt Context-Menü für Queue"""
        try:
            self.queue_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.queue_menu.grab_release()
    
    def refresh_history(self):
        """Aktualisiert History-Anzeige"""
        # Clear tree
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Load history
        history = load_history()
        
        for entry in reversed(history):  # Neueste zuerst
            self.history_tree.insert('', tk.END, values=(
                entry.get('timestamp', ''),
                entry.get('title', ''),
                entry.get('url', '')
            ))
    
    def clear_history(self):
        """Löscht History"""
        if messagebox.askyesno("Bestätigung", "History wirklich löschen?"):
            save_history([])
            self.refresh_history()
            self.add_log("🗑️ History geleert")
    
    def get_current_settings(self):
        """Holt aktuelle Einstellungen aus GUI"""
        return {
            'download_folder': self.folder_var.get(),
            'audio_format': self.audio_format_var.get().split()[0],  # Entfernt Text in Klammern
            'audio_quality': self.audio_quality_var.get().split()[0],
            'download_subtitles': self.download_subtitles_var.get(),
            'subtitle_language': self.subtitle_language_var.get(),
            'speed_limit': self.speed_limit_var.get(),
            'embed_thumbnail': self.embed_thumbnail_var.get(),
            'embed_metadata': self.embed_metadata_var.get(),
            'theme': self.theme_var.get()
        }
    
    def save_settings_gui(self):
        """Speichert Einstellungen"""
        self.settings = self.get_current_settings()
        save_settings(self.settings)
        self.add_log("💾 Einstellungen gespeichert")
        messagebox.showinfo("Erfolg", "Einstellungen wurden gespeichert!")
    
    def update_ytdlp_gui(self):
        """Aktualisiert yt-dlp"""
        self.status_var.set("🔄 Aktualisiere yt-dlp...")
        thread = Thread(target=self._update_ytdlp_thread, daemon=True)
        thread.start()
    
    def _update_ytdlp_thread(self):
        """Thread für yt-dlp Update"""
        success = update_ytdlp()
        
        if success:
            self.root.after(0, lambda: messagebox.showinfo(
                "Erfolg", "yt-dlp wurde erfolgreich aktualisiert!"
            ))
            self.root.after(0, lambda: self.status_var.set("✅ yt-dlp aktualisiert"))
        else:
            self.root.after(0, lambda: messagebox.showerror(
                "Fehler", "yt-dlp konnte nicht aktualisiert werden!"
            ))
            self.root.after(0, lambda: self.status_var.set("❌ Update fehlgeschlagen"))
    
    def check_ffmpeg_startup(self):
        """Prüft FFmpeg beim Start"""
        self.add_log("="*60)
        self.add_log("🚀 Ultimate Music & Video Downloader gestartet")
        self.add_log("="*60)
        
        thread = Thread(target=self._check_ffmpeg_thread, daemon=True)
        thread.start()
    
    def _check_ffmpeg_thread(self):
        """Thread für FFmpeg-Check"""
        if check_ffmpeg():
            self.status_var.set("✅ FFmpeg bereit | Gib eine URL ein")
        else:
            self.status_var.set("❌ FFmpeg nicht verfügbar")
            self.root.after(0, lambda: messagebox.showerror(
                "FFmpeg Fehler", "FFmpeg konnte nicht geladen werden!"
            ))
    
    def add_log(self, message):
        """Fügt Log-Eintrag hinzu"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def process_queues(self):
        """Verarbeitet Message und Progress Queues"""
        # Messages
        while not message_queue.empty():
            msg = message_queue.get()
            self.add_log(msg)
        
        # Progress
        while not progress_queue.empty():
            data = progress_queue.get()
            
            if 'completed' in data and data['completed']:
                self.progress_bar['value'] = 100
                self.progress_var.set("✅ Download abgeschlossen!")
                self.start_download_btn.config(state=tk.NORMAL if self.playlist_data else tk.DISABLED)
                self.download_single_btn.config(state=tk.NORMAL)
                self.load_playlist_btn.config(state=tk.NORMAL)
                self.start_queue_btn.config(state=tk.NORMAL)
                self.stop_download_btn.config(state=tk.DISABLED)
                self.status_var.set("✅ Download abgeschlossen!")
                
                # Refresh history
                self.refresh_history()
            else:
                current = data.get('current', 0)
                total = data.get('total', 1)
                song = data.get('song', '')
                percentage = (current / total) * 100
                
                self.progress_bar['value'] = percentage
                self.progress_var.set(f"{current}/{total} - {song}")
        
        # Schedule next check
        self.root.after(100, self.process_queues)

def main():
    root = tk.Tk()
    app = PlaylistDownloaderApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()
