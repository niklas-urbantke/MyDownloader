import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import os
import re
import yt_dlp
import zipfile
import shutil
import glob
from threading import Thread
from urllib.parse import urlparse, parse_qs
import queue

# Globale Variablen
message_queue = queue.Queue()
progress_queue = queue.Queue()
download_running = False

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
                'songs': songs
            }
    except Exception as e:
        log_message(f"❌ Fehler beim Laden der Playlist: {e}")
        return None

def file_exists(save_dir, artist, title):
    """Prüft, ob ein Song bereits heruntergeladen wurde"""
    filename = f"{clean(artist)} - {clean(title)}.mp3"
    return os.path.exists(os.path.join(save_dir, filename))

def search_and_download(song, save_dir, idx, total):
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
    
    # Prüfe, ob der Song bereits existiert
    if file_exists(save_dir, artist, title):
        log_message(f"⏭️ [{idx}/{total}] Überspringe: {artist} - {title} (bereits vorhanden)")
        return "skipped"
    
    # Dateiname im Format: "Künstler - Titel.mp3"
    output_filename = f"{artist} - {title}.%(ext)s"
    output_path = os.path.join(save_dir, output_filename)
    
    # yt-dlp Optionen
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
    
    # Wenn der Parse fehlgeschlagen ist, nutze Original-Video
    if artist == "Unknown Artist" and original_url:
        clean_original = clean(original_title)
        ydl_opts["outtmpl"] = os.path.join(save_dir, f"{clean_original}.%(ext)s")
        try:
            log_message(f"📥 [{idx}/{total}] Download: {original_title} (Original-Video)")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([original_url])
            log_message(f"✅ [{idx}/{total}] Erfolgreich: {original_title}")
            return True
        except Exception as e:
            log_message(f"❌ [{idx}/{total}] Fehler: {original_title} - {e}")
            return False
    
    # Suche nach Album-Version
    search_query = f"{artist} {title} topic"
    ydl_search = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
    }
    
    try:
        log_message(f"🔍 [{idx}/{total}] Suche: {artist} - {title}")
        
        with yt_dlp.YoutubeDL(ydl_search) as ydl:
            search_results = ydl.extract_info(f"ytsearch5:{search_query}", download=False)
            
            if not search_results or 'entries' not in search_results:
                raise Exception("Keine Suchergebnisse gefunden")
            
            best_match = None
            best_score = 0
            
            for result in search_results['entries']:
                if not result:
                    continue
                
                result_title = result.get('title', '').lower()
                result_channel = result.get('channel', '').lower()
                score = 0
                
                # Scoring-System für beste Übereinstimmung
                if ' - topic' in result_channel or result_channel.endswith(' - topic'):
                    score += 100
                
                if 'provided to youtube' in result_title:
                    score += 90
                
                if 'official audio' in result_title:
                    score += 50
                
                if artist.lower() in result_title and title.lower() in result_title:
                    score += 30
                
                if score > best_score:
                    best_score = score
                    best_match = result
            
            # Fallback auf Original-Video aus Playlist
            if best_score < 30 and original_url:
                log_message(f"📥 [{idx}/{total}] Download: {artist} - {title} (Playlist-Video)")
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([original_url])
            elif best_match:
                video_url = f"https://www.youtube.com/watch?v={best_match['id']}"
                channel = best_match.get('channel', 'YouTube')
                log_message(f"📥 [{idx}/{total}] Download: {artist} - {title} (von {channel})")
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video_url])
            else:
                raise Exception("Kein passendes Video gefunden")
            
            log_message(f"✅ [{idx}/{total}] Erfolgreich: {artist} - {title}")
            return True
            
    except Exception as e:
        log_message(f"❌ [{idx}/{total}] Fehler: {artist} - {title} - {e}")
        return False

def download_playlist_thread(playlist_data):
    """Thread-Funktion für Downloads"""
    global download_running
    download_running = True
    
    playlist_name = playlist_data['name']
    songs = playlist_data['songs']
    
    # Erstelle Ausgabeverzeichnis
    base_dir = os.path.join(os.getcwd(), "Songs", clean(playlist_name))
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
        
        result = search_and_download(song, base_dir, idx, len(songs))
        
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
    
    download_running = False
    progress_queue.put({'completed': True})

def log_message(msg):
    """Fügt Nachricht zur Queue hinzu"""
    message_queue.put(msg)

# GUI-Klasse
class PlaylistDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎵 Music Playlist Downloader")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Stil konfigurieren
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Farben
        bg_color = '#1e1e1e'
        fg_color = '#ffffff'
        accent_color = '#1db954'
        surface_color = '#282828'
        
        self.root.configure(bg=bg_color)
        
        # Header
        header_frame = tk.Frame(self.root, bg=surface_color, height=80)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="🎵 Music Playlist Downloader",
            font=("Segoe UI", 20, "bold"),
            bg=surface_color,
            fg=accent_color
        )
        title_label.pack(pady=20)
        
        # Main Frame
        main_frame = tk.Frame(self.root, bg=bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Input Frame
        input_frame = tk.LabelFrame(
            main_frame,
            text="📋 Playlist URL",
            font=("Segoe UI", 11, "bold"),
            bg=surface_color,
            fg=fg_color,
            relief=tk.FLAT,
            padx=15,
            pady=15
        )
        input_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.url_var = tk.StringVar()
        url_entry = tk.Entry(
            input_frame,
            textvariable=self.url_var,
            font=("Segoe UI", 10),
            bg='#3d3d3d',
            fg=fg_color,
            insertbackground=fg_color,
            relief=tk.FLAT,
            bd=5
        )
        url_entry.pack(fill=tk.X, pady=(0, 10))
        
        button_frame = tk.Frame(input_frame, bg=surface_color)
        button_frame.pack(fill=tk.X)
        
        self.load_btn = tk.Button(
            button_frame,
            text="📥 Playlist laden",
            command=self.load_playlist,
            font=("Segoe UI", 10, "bold"),
            bg=accent_color,
            fg='white',
            activebackground='#1ed760',
            activeforeground='white',
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor='hand2'
        )
        self.load_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.download_btn = tk.Button(
            button_frame,
            text="▶️ Download starten",
            command=self.start_download,
            font=("Segoe UI", 10, "bold"),
            bg='#3d3d3d',
            fg=fg_color,
            activebackground='#4d4d4d',
            activeforeground='white',
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor='hand2',
            state=tk.DISABLED
        )
        self.download_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_btn = tk.Button(
            button_frame,
            text="⏹️ Abbrechen",
            command=self.stop_download,
            font=("Segoe UI", 10, "bold"),
            bg='#e74c3c',
            fg='white',
            activebackground='#c0392b',
            activeforeground='white',
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor='hand2',
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT)
        
        # Progress Frame
        progress_frame = tk.LabelFrame(
            main_frame,
            text="📊 Fortschritt",
            font=("Segoe UI", 11, "bold"),
            bg=surface_color,
            fg=fg_color,
            relief=tk.FLAT,
            padx=15,
            pady=15
        )
        progress_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.progress_var = tk.StringVar(value="Bereit")
        progress_label = tk.Label(
            progress_frame,
            textvariable=self.progress_var,
            font=("Segoe UI", 10),
            bg=surface_color,
            fg=fg_color
        )
        progress_label.pack(anchor=tk.W, pady=(0, 5))
        
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
            font=("Segoe UI", 11, "bold"),
            bg=surface_color,
            fg=fg_color,
            relief=tk.FLAT,
            padx=15,
            pady=15
        )
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            font=("Consolas", 9),
            bg='#0d0d0d',
            fg='#00ff00',
            insertbackground='#00ff00',
            relief=tk.FLAT,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Status Bar
        status_frame = tk.Frame(self.root, bg=surface_color, height=30)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)
        
        self.status_var = tk.StringVar(value="Bereit")
        status_label = tk.Label(
            status_frame,
            textvariable=self.status_var,
            font=("Segoe UI", 9),
            bg=surface_color,
            fg=fg_color,
            anchor=tk.W
        )
        status_label.pack(fill=tk.X, padx=10, pady=5)
        
        # Daten
        self.playlist_data = None
        
        # Start FFmpeg Check
        self.check_ffmpeg_startup()
        
        # Start Queue Processing
        self.process_queues()
    
    def check_ffmpeg_startup(self):
        """Prüft FFmpeg beim Start"""
        self.add_log("="*60)
        self.add_log("🚀 Music Playlist Downloader gestartet")
        self.add_log("="*60)
        
        thread = Thread(target=self._check_ffmpeg_thread, daemon=True)
        thread.start()
    
    def _check_ffmpeg_thread(self):
        """Thread für FFmpeg-Check"""
        if check_ffmpeg():
            self.status_var.set("✅ FFmpeg bereit | Gib eine Playlist-URL ein")
        else:
            self.status_var.set("❌ FFmpeg nicht verfügbar")
            messagebox.showerror("FFmpeg Fehler", "FFmpeg konnte nicht geladen werden!")
    
    def add_log(self, message):
        """Fügt Log-Eintrag hinzu"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def load_playlist(self):
        """Lädt Playlist-Informationen"""
        url = self.url_var.get().strip()
        
        if not url:
            messagebox.showwarning("Fehler", "Bitte eine URL eingeben!")
            return
        
        self.load_btn.config(state=tk.DISABLED)
        self.status_var.set("⏳ Lade Playlist...")
        
        thread = Thread(target=self._load_playlist_thread, args=(url,), daemon=True)
        thread.start()
    
    def _load_playlist_thread(self, url):
        """Thread für Playlist-Laden"""
        self.playlist_data = get_youtube_playlist(url)
        
        if self.playlist_data:
            self.root.after(0, lambda: self.download_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.status_var.set(
                f"✅ Playlist geladen: {self.playlist_data['name']} ({len(self.playlist_data['songs'])} Songs)"
            ))
        else:
            self.root.after(0, lambda: messagebox.showerror(
                "Fehler", "Playlist konnte nicht geladen werden!"
            ))
            self.root.after(0, lambda: self.status_var.set("❌ Fehler beim Laden"))
        
        self.root.after(0, lambda: self.load_btn.config(state=tk.NORMAL))
    
    def start_download(self):
        """Startet Download"""
        if not self.playlist_data:
            messagebox.showwarning("Fehler", "Bitte zuerst eine Playlist laden!")
            return
        
        self.download_btn.config(state=tk.DISABLED)
        self.load_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.progress_bar['value'] = 0
        self.status_var.set("▶️ Download läuft...")
        
        thread = Thread(target=download_playlist_thread, args=(self.playlist_data,), daemon=True)
        thread.start()
    
    def stop_download(self):
        """Stoppt Download"""
        global download_running
        download_running = False
        self.stop_btn.config(state=tk.DISABLED)
        self.status_var.set("⏹️ Download wird abgebrochen...")
    
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
                self.download_btn.config(state=tk.NORMAL)
                self.load_btn.config(state=tk.NORMAL)
                self.stop_btn.config(state=tk.DISABLED)
                self.status_var.set("✅ Download abgeschlossen!")
            else:
                current = data.get('current', 0)
                total = data.get('total', 1)
                song = data.get('song', '')
                percentage = (current / total) * 100
                
                self.progress_bar['value'] = percentage
                self.progress_var.set(f"{current}/{total} Songs - {song}")
        
        # Schedule next check
        self.root.after(100, self.process_queues)

def main():
    root = tk.Tk()
    app = PlaylistDownloaderApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()
