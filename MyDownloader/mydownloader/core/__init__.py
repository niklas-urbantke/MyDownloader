"""
Core Package - Download Logic
"""

from .ffmpeg import FFmpegManager
from .youtube import YouTubeDownloader
from .downloader import Downloader
from .queue_manager import QueueManager

__all__ = ['FFmpegManager', 'YouTubeDownloader', 'Downloader', 'QueueManager']
