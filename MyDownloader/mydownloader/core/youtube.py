"""
YouTube Downloader Module
"""

import yt_dlp
import re
from typing import Dict, List, Optional, Callable
from urllib.parse import urlparse, parse_qs
from ..utils.logger import get_logger
from ..utils.validators import is_youtube_url, is_youtube_playlist

logger = get_logger(__name__)


class YouTubeDownloader:
    """Handle YouTube video and playlist downloads"""
    
    def __init__(self):
        self.ydl_opts_base = {
            'quiet': True,
            'no_warnings': True,
        }
    
    def get_video_info(self, url: str) -> Optional[Dict]:
        """
        Get video information without downloading
        
        Args:
            url: Video URL
            
        Returns:
            Dict with video info or None
        """
        if not is_youtube_url(url):
            logger.error(f"Invalid YouTube URL: {url}")
            return None
        
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts_base) as ydl:
                info = ydl.extract_info(url, download=False)
                
                return {
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'thumbnail': info.get('thumbnail', ''),
                    'uploader': info.get('uploader', 'Unknown'),
                    'view_count': info.get('view_count', 0),
                    'description': info.get('description', ''),
                    'upload_date': info.get('upload_date', ''),
                    'url': url,
                    'id': info.get('id', '')
                }
        except Exception as e:
            logger.error(f"Failed to get video info: {e}")
            return None
    
    def get_playlist_info(self, url: str) -> Optional[Dict]:
        """
        Get playlist information
        
        Args:
            url: Playlist URL
            
        Returns:
            Dict with playlist info or None
        """
        if not is_youtube_playlist(url):
            logger.error(f"Invalid YouTube playlist URL: {url}")
            return None
        
        # Extract playlist ID
        parsed = urlparse(url)
        if "list=" in url:
            query_params = parse_qs(parsed.query)
            playlist_id = query_params.get("list", [None])[0]
            if playlist_id:
                url = f"https://www.youtube.com/playlist?list={playlist_id}"
        
        opts = {
            **self.ydl_opts_base,
            'extract_flat': True,
            'yes_playlist': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if 'entries' not in info:
                    return None
                
                playlist_name = info.get('title', 'YouTube Playlist')
                videos = []
                
                for entry in info['entries']:
                    if entry:
                        video_id = entry.get('id', '')
                        video_url = f"https://www.youtube.com/watch?v={video_id}"
                        video_title = entry.get('title', 'Unknown')
                        
                        # Parse artist and title
                        artist, title = self._parse_video_title(video_title)
                        
                        videos.append({
                            'id': video_id,
                            'url': video_url,
                            'title': video_title,
                            'artist': artist,
                            'song_title': title
                        })
                
                logger.info(f"Loaded playlist: {playlist_name} ({len(videos)} videos)")
                
                return {
                    'name': playlist_name,
                    'url': url,
                    'video_count': len(videos),
                    'videos': videos
                }
                
        except Exception as e:
            logger.error(f"Failed to get playlist info: {e}")
            return None
    
    def _parse_video_title(self, title: str) -> tuple:
        """
        Parse video title to extract artist and song name
        
        Args:
            title: Video title
            
        Returns:
            Tuple of (artist, song_title)
        """
        original = title
        
        # Remove common suffixes
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
        ]
        
        for pattern in patterns:
            title = re.sub(pattern, '', title, flags=re.IGNORECASE)
        
        title = title.strip()
        
        # Try to extract "Artist - Title" format
        if ' - ' in title:
            parts = title.split(' - ', 1)
            return parts[0].strip(), parts[1].strip()
        
        return "Unknown Artist", original
    
    @staticmethod
    def update_ytdlp() -> bool:
        """
        Update yt-dlp to latest version
        
        Returns:
            True if successful
        """
        import subprocess
        try:
            logger.info("Updating yt-dlp...")
            result = subprocess.run(
                ['pip', 'install', '--upgrade', 'yt-dlp'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                logger.info("yt-dlp updated successfully")
                return True
            else:
                logger.error(f"Update failed: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Failed to update yt-dlp: {e}")
            return False


# Global instance
youtube_downloader = YouTubeDownloader()
