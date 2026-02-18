"""
FFmpeg Manager - Handles FFmpeg installation and management
"""

import os
import shutil
import zipfile
import glob
from typing import Optional
import urllib.request
from ..constants import FFMPEG_DOWNLOAD_URL, FFMPEG_DIR, FFMPEG_BIN_DIR
from ..utils.logger import get_logger

logger = get_logger(__name__)


class FFmpegManager:
    """Manage FFmpeg installation and availability"""
    
    def __init__(self):
        self._ffmpeg_path: Optional[str] = None
        self._ffprobe_path: Optional[str] = None
        self._is_available = False
    
    def check_availability(self) -> bool:
        """
        Check if FFmpeg is available
        
        Returns:
            True if FFmpeg is available
        """
        logger.info("Checking FFmpeg availability...")
        
        # Check portable version first
        if self._check_portable():
            self._is_available = True
            logger.info("FFmpeg found (portable version)")
            return True
        
        # Check system installation
        if self._check_system():
            self._is_available = True
            logger.info("FFmpeg found (system installation)")
            return True
        
        # Try to download and install
        logger.warning("FFmpeg not found, attempting download...")
        if self.download_portable():
            self._is_available = True
            return True
        
        logger.error("FFmpeg not available")
        self._is_available = False
        return False
    
    def _check_portable(self) -> bool:
        """Check for portable FFmpeg in application directory"""
        ffmpeg_exe = os.path.join(FFMPEG_BIN_DIR, "ffmpeg.exe")
        ffprobe_exe = os.path.join(FFMPEG_BIN_DIR, "ffprobe.exe")
        
        if os.path.exists(ffmpeg_exe) and os.path.exists(ffprobe_exe):
            self._ffmpeg_path = ffmpeg_exe
            self._ffprobe_path = ffprobe_exe
            self._add_to_path(FFMPEG_BIN_DIR)
            return True
        
        return False
    
    def _check_system(self) -> bool:
        """Check for system-installed FFmpeg"""
        # Check in PATH
        ffmpeg = shutil.which("ffmpeg")
        ffprobe = shutil.which("ffprobe")
        
        if ffmpeg and ffprobe:
            self._ffmpeg_path = ffmpeg
            self._ffprobe_path = ffprobe
            return True
        
        # Check common installation directories (Windows)
        possible_paths = [
            r"C:\Program Files\ffmpeg\bin",
            r"C:\ffmpeg\bin",
            r"C:\ProgramData\chocolatey\bin",
        ]
        
        # Check WinGet installations
        winget_pattern = os.path.expanduser(
            r"~\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg*\ffmpeg-*\bin"
        )
        possible_paths.extend(glob.glob(winget_pattern))
        
        for path in possible_paths:
            if os.path.exists(path):
                ffmpeg_test = os.path.join(path, "ffmpeg.exe")
                ffprobe_test = os.path.join(path, "ffprobe.exe")
                
                if os.path.exists(ffmpeg_test) and os.path.exists(ffprobe_test):
                    self._ffmpeg_path = ffmpeg_test
                    self._ffprobe_path = ffprobe_test
                    self._add_to_path(path)
                    logger.info(f"Found FFmpeg at: {path}")
                    return True
        
        return False
    
   def _add_to_path(self, directory: str) -> None:
        """Add directory to PATH environment variable"""
        current_path = os.environ.get("PATH", "")
        if directory not in current_path:
            os.environ["PATH"] = directory + os.pathsep + current_path
            logger.debug(f"Added {directory} to PATH")
    
    def download_portable(self, progress_callback=None) -> bool:
        """
        Download and install portable FFmpeg
        
        Args:
            progress_callback: Optional callback for progress updates
            
        Returns:
            True if successful
        """
        try:
            logger.info("Downloading portable FFmpeg...")
            
            zip_path = "ffmpeg-temp.zip"
            
            # Download
            if progress_callback:
                progress_callback("Downloading FFmpeg (75 MB)...")
            
            urllib.request.urlretrieve(FFMPEG_DOWNLOAD_URL, zip_path)
            
            # Extract
            if progress_callback:
                progress_callback("Extracting FFmpeg...")
            
            logger.info("Extracting FFmpeg...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                for member in zip_ref.namelist():
                    if '/bin/' in member and member.endswith('.exe'):
                        filename = os.path.basename(member)
                        target_path = os.path.join(FFMPEG_BIN_DIR, filename)
                        os.makedirs(FFMPEG_BIN_DIR, exist_ok=True)
                        
                        with zip_ref.open(member) as source:
                            with open(target_path, 'wb') as target:
                                target.write(source.read())
            
            # Cleanup
            os.remove(zip_path)
            
            logger.info("FFmpeg successfully downloaded and installed")
            
            # Verify installation
            if self._check_portable():
                if progress_callback:
                    progress_callback("FFmpeg ready!")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to download FFmpeg: {e}")
            if progress_callback:
                progress_callback(f"Error: {e}")
            return False
    
    @property
    def is_available(self) -> bool:
        """Check if FFmpeg is available"""
        return self._is_available
    
    @property
    def ffmpeg_path(self) -> Optional[str]:
        """Get FFmpeg executable path"""
        return self._ffmpeg_path
    
    @property
    def ffprobe_path(self) -> Optional[str]:
        """Get FFprobe executable path"""
        return self._ffprobe_path


# Global instance
ffmpeg_manager = FFmpegManager()
