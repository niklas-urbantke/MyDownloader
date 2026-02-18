from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import os
import re
import yt_dlp
import zipfile
import requests
import shutil
import glob
from threading import Thread
from urllib.parse import urlparse, parse_qs
import socket
import webbrowser
import tkinter as tk
from tkinter import ttk

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app, cors_allowed_origins="*")

# Fortschrittsstatus
download_status = {
    'current': 0,
    'total': 0,
    'current_song': '',
    'status': 'idle',
    'playlist_name': ''
}

def clean(text):
    """Entfernt unerlaubte Zeichen aus Dateinamen"""
    return re.sub(r'[<>:"/\\|?*]', '', text)

def download_ffmpeg_portable():
    """Lädt FFmpeg herunter und entpackt es im Projektordner"""
    socketio.emit('status_update', {'message': '🔄 Lade portable FFmpeg herunter...'})
    
    ffmpeg_dir = os.path.join(os.getcwd(), "ffmpeg")
    bin_dir = os.path.join(ffmpeg_dir, "bin")
    
    # Prüfe ob schon vorhanden
    if os.path.exists(os.path.join(bin_dir, "ffmpeg.exe")):
        socketio.emit('status_update', {'message': '✅ Portable FFmpeg bereits vorhanden!'})
        return bin_dir
    
    try:
        import urllib.request
        
        # Download URL für FFmpeg essentials build
        url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
        zip_path = "ffmpeg-temp.zip"
        
        socketio.emit('status_update', {'message': '📥 Downloading FFmpeg... (ca. 75 MB)'})
        urllib.request.urlretrieve(url, zip_path)
        
        socketio.emit('status_update', {'message': '📦 Entpacke FFmpeg...'})
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
        
        socketio.emit('status_update', {'message': '✅ FFmpeg erfolgreich heruntergeladen!'})
        return bin_dir
        
    except Exception as e:
        socketio.emit('error', {'message': f'❌ FFmpeg-Download fehlgeschlagen: {e}'})
        return None

def check_ffmpeg():
    """Prüft, ob FFmpeg verfügbar ist"""
    # Prüfe zuerst im Projektordner (portable Version)
    local_ffmpeg = os.path.join(os.getcwd(), "ffmpeg", "bin")
    local_ffmpeg_exe = os.path.join(local_ffmpeg, "ffmpeg.exe")
    
    if os.path.exists(local_ffmpeg_exe):
        # Füge zum PATH hinzu für diese Session
        os.environ["PATH"] = local_ffmpeg + os.pathsep + os.environ.get("PATH", "")
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
                    return True
    
    if ffmpeg_path and ffprobe_path:
        return True
    
    # FFmpeg nicht gefunden - lade portable Version herunter
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
    socketio.emit('status_update', {'message': 'Lade Playlist-Informationen...'})
    
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
            
            return {
                'name': playlist_name,
                'songs': songs
            }
    except Exception as e:
        socketio.emit('error', {'message': f'Fehler beim Laden der Playlist: {str(e)}'})
        return None

def file_exists(save_dir, artist, title):
    """Prüft, ob ein Song bereits heruntergeladen wurde"""
    filename = f"{clean(artist)} - {clean(title)}.mp3"
    return os.path.exists(os.path.join(save_dir, filename))

def search_and_download(song, save_dir):
    """Sucht und lädt einen Song herunter"""
    artist = clean(song["artist"])
    title = clean(song["title"])
    original_url = song.get("original_url", None)
    original_title = song.get("original_title", "")
    
    # Prüfe, ob der Song bereits existiert
    if file_exists(save_dir, artist, title):
        socketio.emit('song_status', {
            'song': f"{artist} - {title}",
            'status': 'skipped',
            'message': 'Bereits vorhanden'
        })
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
            socketio.emit('song_status', {
                'song': original_title,
                'status': 'downloading',
                'message': 'Nutze Original-Video'
            })
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([original_url])
            socketio.emit('song_status', {
                'song': original_title,
                'status': 'success',
                'message': 'Erfolgreich heruntergeladen'
            })
            return True
        except Exception as e:
            socketio.emit('song_status', {
                'song': original_title,
                'status': 'error',
                'message': str(e)
            })
            return False
    
    # Suche nach Album-Version
    search_query = f"{artist} {title} topic"
    ydl_search = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
    }
    
    try:
        socketio.emit('song_status', {
            'song': f"{artist} - {title}",
            'status': 'searching',
            'message': 'Suche nach Album-Version...'
        })
        
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
                socketio.emit('song_status', {
                    'song': f"{artist} - {title}",
                    'status': 'downloading',
                    'message': 'Nutze Playlist-Video (keine bessere Version gefunden)'
                })
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([original_url])
            elif best_match:
                video_url = f"https://www.youtube.com/watch?v={best_match['id']}"
                socketio.emit('song_status', {
                    'song': f"{artist} - {title}",
                    'status': 'downloading',
                    'message': f'Download von: {best_match.get("channel", "YouTube")}'
                })
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video_url])
            else:
                raise Exception("Kein passendes Video gefunden")
            
            socketio.emit('song_status', {
                'song': f"{artist} - {title}",
                'status': 'success',
                'message': 'Erfolgreich heruntergeladen'
            })
            return True
            
    except Exception as e:
        socketio.emit('song_status', {
            'song': f"{artist} - {title}",
            'status': 'error',
            'message': str(e)
        })
        return False

def download_thread(playlist_data):
    """Thread-Funktion für Downloads"""
    global download_status
    
    playlist_name = playlist_data['name']
    songs = playlist_data['songs']
    
    # Erstelle Ausgabeverzeichnis
    base_dir = os.path.join(os.getcwd(), "Songs", clean(playlist_name))
    os.makedirs(base_dir, exist_ok=True)
    
    download_status['total'] = len(songs)
    download_status['current'] = 0
    download_status['playlist_name'] = playlist_name
    download_status['status'] = 'downloading'
    
    socketio.emit('download_started', {
        'total': len(songs),
        'playlist_name': playlist_name
    })
    
    for idx, song in enumerate(songs, 1):
        download_status['current'] = idx
        download_status['current_song'] = f"{song['artist']} - {song['title']}"
        
        socketio.emit('progress_update', {
            'current': idx,
            'total': len(songs),
            'percentage': int((idx / len(songs)) * 100),
            'current_song': download_status['current_song']
        })
        
        search_and_download(song, base_dir)
    
    download_status['status'] = 'completed'
    socketio.emit('download_completed', {
        'total': len(songs),
        'folder': base_dir
    })

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check_ffmpeg', methods=['GET'])
def check_ffmpeg_route():
    return jsonify({'available': check_ffmpeg()})

@app.route('/load_playlist', methods=['POST'])
def load_playlist():
    data = request.json
    url = data.get('url', '')
    
    if not url:
        return jsonify({'error': 'Keine URL angegeben'}), 400
    
    playlist_data = get_youtube_playlist(url)
    
    if not playlist_data:
        return jsonify({'error': 'Playlist konnte nicht geladen werden'}), 400
    
    return jsonify({
        'success': True,
        'playlist_name': playlist_data['name'],
        'song_count': len(playlist_data['songs']),
        'songs': [f"{s['artist']} - {s['title']}" for s in playlist_data['songs'][:10]]
    })

@app.route('/start_download', methods=['POST'])
def start_download():
    global download_status
    
    if download_status['status'] == 'downloading':
        return jsonify({'error': 'Download läuft bereits'}), 400
    
    data = request.json
    url = data.get('url', '')
    
    if not url:
        return jsonify({'error': 'Keine URL angegeben'}), 400
    
    if not check_ffmpeg():
        return jsonify({'error': 'FFmpeg nicht verfügbar'}), 400
    
    playlist_data = get_youtube_playlist(url)
    
    if not playlist_data:
        return jsonify({'error': 'Playlist konnte nicht geladen werden'}), 400
    
    # Starte Download in separatem Thread
    thread = Thread(target=download_thread, args=(playlist_data,))
    thread.daemon = True
    thread.start()
    
    return jsonify({'success': True})

@app.route('/status', methods=['GET'])
def status():
    return jsonify(download_status)

def find_free_port():
    """Findet einen freien Port"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port

def start_flask_server(port):
    """Startet Flask-Server in separatem Thread"""
    socketio.run(app, debug=False, host='127.0.0.1', port=port, use_reloader=False, log_output=False)

def create_control_window(url, port):
    """Erstellt Tkinter Control Window"""
    root = tk.Tk()
    root.title("Music Playlist Downloader - Control Panel")
    root.geometry("500x400")
    root.resizable(False, False)
    
    # Setze Icon und Farben
    root.configure(bg='#1e1e1e')
    
    # Stil konfigurieren
    style = ttk.Style()
    style.theme_use('clam')
    style.configure('Custom.TFrame', background='#1e1e1e')
    style.configure('Custom.TLabel', background='#1e1e1e', foreground='#ffffff', font=('Segoe UI', 10))
    style.configure('Title.TLabel', background='#1e1e1e', foreground='#1db954', font=('Segoe UI', 16, 'bold'))
    style.configure('Custom.TButton', background='#1db954', foreground='#ffffff', font=('Segoe UI', 10, 'bold'), borderwidth=0)
    style.map('Custom.TButton', background=[('active', '#1ed760')])
    
    # Hauptframe
    main_frame = ttk.Frame(root, style='Custom.TFrame', padding=30)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Logo und Titel
    title = ttk.Label(main_frame, text="🎵 Music Playlist Downloader", style='Title.TLabel')
    title.pack(pady=(0, 20))
    
    # Status-Bereich
    status_frame = ttk.Frame(main_frame, style='Custom.TFrame')
    status_frame.pack(fill=tk.X, pady=20)
    
    status_label = ttk.Label(status_frame, text="✅ Server läuft", style='Custom.TLabel', font=('Segoe UI', 12))
    status_label.pack()
    
    url_label = ttk.Label(status_frame, text=url, style='Custom.TLabel', foreground='#b3b3b3')
    url_label.pack(pady=5)
    
    port_label = ttk.Label(status_frame, text=f"Port: {port}", style='Custom.TLabel', foreground='#b3b3b3')
    port_label.pack()
    
    # Separator
    separator = ttk.Separator(main_frame, orient='horizontal')
    separator.pack(fill=tk.X, pady=20)
    
    # Button-Bereich
    button_frame = ttk.Frame(main_frame, style='Custom.TFrame')
    button_frame.pack(fill=tk.X)
    
    def open_browser():
        webbrowser.open(url)
    
    def close_app():
        root.quit()
        os._exit(0)
    
    # Buttons mit Custom-Style
    open_btn = tk.Button(
        button_frame, 
        text="🌐 Browser öffnen", 
        command=open_browser,
        bg='#1db954',
        fg='white',
        font=('Segoe UI', 11, 'bold'),
        relief=tk.FLAT,
        padx=20,
        pady=12,
        cursor='hand2',
        activebackground='#1ed760',
        activeforeground='white'
    )
    open_btn.pack(fill=tk.X, pady=5)
    
    close_btn = tk.Button(
        button_frame,
        text="❌ App beenden",
        command=close_app,
        bg='#282828',
        fg='white',
        font=('Segoe UI', 11, 'bold'),
        relief=tk.FLAT,
        padx=20,
        pady=12,
        cursor='hand2',
        activebackground='#3d3d3d',
        activeforeground='white'
    )
    close_btn.pack(fill=tk.X, pady=5)
    
    # Info-Text
    info_frame = ttk.Frame(main_frame, style='Custom.TFrame')
    info_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(20, 0))
    
    info_text = ttk.Label(
        info_frame,
        text="Die Web-GUI läuft in deinem Browser.\nSchließe dieses Fenster, um die App zu beenden.",
        style='Custom.TLabel',
        foreground='#b3b3b3',
        font=('Segoe UI', 9),
        justify=tk.CENTER
    )
    info_text.pack()
    
    # Öffne Browser automatisch beim Start
    root.after(1000, open_browser)
    
    # Beim Schließen des Fensters die App beenden
    root.protocol("WM_DELETE_WINDOW", close_app)
    
    root.mainloop()

if __name__ == '__main__':
    # Finde freien Port
    port = find_free_port()
    url = f'http://127.0.0.1:{port}'
    
    # Starte Flask-Server in separatem Thread
    flask_thread = Thread(target=start_flask_server, args=(port,))
    flask_thread.daemon = True
    flask_thread.start()
    
    # Warte kurz, bis Server bereit ist
    import time
    time.sleep(1.5)
    
    # Erstelle Control Window
    create_control_window(url, port)
