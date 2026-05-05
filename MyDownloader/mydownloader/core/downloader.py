"""
Main Downloader Module
"""

import os
import yt_dlp
from typing import Optional, Callable, Dict
from ..utils.logger import get_logger
from ..utils.file_utils import clean_filename, ensure_directory
from ..data.history import history_manager

logger = get_logger(__name__)


class Downloader:
    """Main download handler"""
    
    def __init__(self):
        self.is_downloading = False
        self.should_stop = False
    
    def download(self, url: str, output_dir: str, settings: Dict,
                 progress_callback: Optional[Callable] = None,
                 log_callback: Optional[Callable] = None) -> bool:
        """
        Download video/audio from URL
        
        Args:
            url: Video URL
            output_dir: Output directory
            settings: Download settings dict
            progress_callback: Progress callback function
            log_callback: Log callback function
            
        Returns:
            True if successful
        """
        self.is_downloading = True
        self.should_stop = False
        
        try:
            # Ensure output directory exists
            ensure_directory(output_dir)
            
            # Build yt-dlp options
            ydl_opts = self._build_options(output_dir, settings)
            
            # Add progress hook
            if progress_callback:
                ydl_opts['progress_hooks'] = [
                    lambda d: self._progress_hook(d, progress_callback)
                ]
            
            # Log start
            if log_callback:
                log_callback(f"Downloading: {url}")
            
            logger.info(f"Starting download: {url}")
            
            # Download
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get('title', 'Unknown')
                
                if log_callback:
                    log_callback(f"✅ Completed: {title}")
                
                # Add to history
                history_manager.add_entry(url, title, 'video', 'completed')
                
                logger.info(f"Download completed: {title}")
                return True
                
        except Exception as e:
            logger.error(f"Download failed: {e}")
            if log_callback:
                log_callback(f"❌ Error: {e}")
            return False
        finally:
            self.is_downloading = False
    
    def _build_options(self, output_dir: str, settings: Dict) -> Dict:
        """Build yt-dlp options from settings"""
        output_template = os.path.join(output_dir, "%(title)s.%(ext)s")
        
        opts = {
            "outtmpl": output_template,
            "quiet": False,
            "no_warnings": False,
            "continuedl": True,
            "retries": 10,
        }
        
        # Format settings
        audio_format = settings.get('audio_format', 'mp3')
        if audio_format == 'mp4':
            opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
            opts['merge_output_format'] = 'mp4'
        elif audio_format and audio_format != 'none':
            opts['format'] = 'bestaudio/best'
            opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': audio_format,
                'preferredquality': settings.get('audio_quality', '0'),
            }]
            
            # Thumbnail embedding
            if settings.get('embed_thumbnail'):
                opts['postprocessors'].append({'key': 'EmbedThumbnail'})
                opts['writethumbnail'] = True
            
            # Metadata embedding
            if settings.get('embed_metadata'):
                opts['postprocessors'].append({'key': 'FFmpegMetadata'})
        else:
            # Video mode
            opts['format'] = 'bestvideo+bestaudio/best'
        
        # Subtitles
        if settings.get('download_subtitles'):
            opts['writesubtitles'] = True
            opts['subtitleslangs'] = settings.get('subtitle_language', 'de,en').split(',')
            opts['subtitlesformat'] = 'srt'
        
        # Speed limit
        speed_limit = settings.get('speed_limit', '')
        if speed_limit:
            try:
                opts['ratelimit'] = int(float(speed_limit) * 1024 * 1024)
            except ValueError:
                pass
        
        return opts
    
    def _progress_hook(self, d: Dict, callback: Callable) -> None:
        """Handle download progress"""
        if d['status'] == 'downloading':
            try:
                percent = d.get('_percent_str', '0%').strip()
                speed = d.get('_speed_str', 'N/A')
                eta = d.get('_eta_str', 'N/A')
                callback(f"Progress: {percent} | Speed: {speed} | ETA: {eta}")
            except:
                pass
    
    def stop(self) -> None:
        """Stop current download"""
        self.should_stop = True
        logger.info("Download stop requested")


# Global instance
downloader = Downloader()
