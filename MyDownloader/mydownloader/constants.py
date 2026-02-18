"""
Application Constants
"""

import os

# Application
APP_NAME = "MyDownloader"
APP_VERSION = "3.0.0"
APP_DESCRIPTION = "Ultimate Music & Video Downloader"
APP_AUTHOR = "UST-Germany"

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(os.path.expanduser("~"), ".mydownloader")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")
LOG_FILE = os.path.join(DATA_DIR, "app.log")

# Default Settings
DEFAULT_SETTINGS = {
    "download_folder": os.path.join(os.getcwd(), "Downloads"),
    "audio_format": "mp3",
    "audio_quality": "0",
    "download_subtitles": False,
    "subtitle_language": "de,en",
    "speed_limit": "",
    "theme": "dark",
    "embed_thumbnail": True,
    "embed_metadata": True,
    "keep_video": False,
    "concurrent_downloads": 1,
    "auto_update": True,
    "notification_enabled": True
}

# Audio Formats
AUDIO_FORMATS = {
    'mp3': 'MP3 (MPEG Audio Layer III)',
    'm4a': 'M4A (MPEG-4 Audio)',
    'opus': 'OPUS (Opus Audio)',
    'flac': 'FLAC (Lossless)',
    'wav': 'WAV (Uncompressed)',
    'none': 'None (Video only)'
}

# Audio Quality
AUDIO_QUALITY_OPTIONS = {
    '0': '0 (Beste Qualität)',
    '2': '2 (Sehr gut)',
    '5': '5 (Gut)',
    '7': '7 (Akzeptabel)',
    '9': '9 (Kleinste Datei)'
}

# Themes
THEMES = {
    'dark': {
        'bg_color': '#1e1e1e',
        'fg_color': '#ffffff',
        'accent_color': '#1db954',
        'surface_color': '#282828',
        'error_color': '#e74c3c',
        'success_color': '#4CAF50',
        'warning_color': '#FF9800'
    },
    'light': {
        'bg_color': '#f0f0f0',
        'fg_color': '#000000',
        'accent_color': '#0078d4',
        'surface_color': '#ffffff',
        'error_color': '#c0392b',
        'success_color': '#27ae60',
        'warning_color': '#f39c12'
    }
}

# YouTube
YOUTUBE_DOMAINS = [
    'youtube.com',
    'youtu.be',
    'youtube-nocookie.com',
    'm.youtube.com'
]

# FFmpeg
FFMPEG_DOWNLOAD_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
FFMPEG_DIR = os.path.join(os.getcwd(), "ffmpeg")
FFMPEG_BIN_DIR = os.path.join(FFMPEG_DIR, "bin")

# Logging
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
LOG_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
LOG_BACKUP_COUNT = 5

# History
MAX_HISTORY_ENTRIES = 100

# UI
WINDOW_MIN_WIDTH = 1000
WINDOW_MIN_HEIGHT = 700
WINDOW_DEFAULT_WIDTH = 1100
WINDOW_DEFAULT_HEIGHT = 800

# Icons (Unicode)
ICON_DOWNLOAD = "📥"
ICON_QUEUE = "📑"
ICON_HISTORY = "📜"
ICON_SETTINGS = "⚙️"
ICON_INFO = "ℹ️"
ICON_MUSIC = "🎵"
ICON_VIDEO = "📹"
ICON_FOLDER = "📁"
ICON_SUCCESS = "✅"
ICON_ERROR = "❌"
ICON_WARNING = "⚠️"
ICON_LOADING = "⏳"
ICON_SEARCH = "🔍"
ICON_PREVIEW = "👁️"

# Status Messages
STATUS_READY = "Bereit"
STATUS_LOADING = "Lädt..."
STATUS_DOWNLOADING = "Download läuft..."
STATUS_COMPLETED = "Abgeschlossen!"
STATUS_ERROR = "Fehler aufgetreten"
STATUS_CANCELLED = "Abgebrochen"
