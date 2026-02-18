"""
Input Validators
"""

import re
from urllib.parse import urlparse
from typing import Optional
from ..constants import YOUTUBE_DOMAINS
from .logger import get_logger

logger = get_logger(__name__)


def is_valid_url(url: str) -> bool:
    """
    Check if string is a valid URL
    
    Args:
        url: URL string to validate
        
    Returns:
        True if valid URL
    """
    if not url or not isinstance(url, str):
        return False
    
    try:
        result = urlparse(url.strip())
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def is_youtube_url(url: str) -> bool:
    """
    Check if URL is a YouTube URL
    
    Args:
        url: URL string to check
        
    Returns:
        True if YouTube URL
    """
    if not is_valid_url(url):
        return False
    
    try:
        parsed = urlparse(url.strip())
        domain = parsed.netloc.lower()
        
        # Remove www. prefix
        if domain.startswith('www.'):
            domain = domain[4:]
        
        return any(youtube_domain in domain for youtube_domain in YOUTUBE_DOMAINS)
    except Exception:
        return False


def is_youtube_playlist(url: str) -> bool:
    """
    Check if URL is a YouTube playlist
    
    Args:
        url: URL string to check
        
    Returns:
        True if YouTube playlist URL
    """
    if not is_youtube_url(url):
        return False
    
    return 'list=' in url.lower()


def extract_youtube_video_id(url: str) -> Optional[str]:
    """
    Extract YouTube video ID from URL
    
    Args:
        url: YouTube URL
        
    Returns:
        Video ID or None
    """
    if not is_youtube_url(url):
        return None
    
    # Pattern for various YouTube URL formats
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:embed\/)([0-9A-Za-z_-]{11})',
        r'^([0-9A-Za-z_-]{11})$'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None


def extract_youtube_playlist_id(url: str) -> Optional[str]:
    """
    Extract YouTube playlist ID from URL
    
    Args:
        url: YouTube playlist URL
        
    Returns:
        Playlist ID or None
    """
    if not is_youtube_playlist(url):
        return None
    
    match = re.search(r'list=([^&]+)', url)
    if match:
        return match.group(1)
    
    return None


def validate_audio_format(format_str: str) -> bool:
    """
    Validate audio format string
    
    Args:
        format_str: Audio format
        
    Returns:
        True if valid
    """
    valid_formats = ['mp3', 'm4a', 'opus', 'flac', 'wav', 'none']
    return format_str.lower() in valid_formats


def validate_audio_quality(quality: str) -> bool:
    """
    Validate audio quality string
    
    Args:
        quality: Quality setting (0-9)
        
    Returns:
        True if valid
    """
    try:
        q = int(quality)
        return 0 <= q <= 9
    except ValueError:
        return False


def validate_speed_limit(limit: str) -> bool:
    """
    Validate speed limit string
    
    Args:
        limit: Speed limit (empty string or positive number)
        
    Returns:
        True if valid
    """
    if not limit or limit.strip() == '':
        return True
    
    try:
        value = float(limit)
        return value > 0
    except ValueError:
        return False


def sanitize_subtitle_languages(languages: str) -> str:
    """
    Sanitize subtitle language string
    
    Args:
        languages: Comma-separated language codes
        
    Returns:
        Sanitized language string
    """
    if not languages:
        return ''
    
    # Split by comma, strip whitespace, remove empty
    langs = [lang.strip().lower() for lang in languages.split(',') if lang.strip()]
    
    # Validate language codes (2-3 letter codes)
    valid_langs = [lang for lang in langs if re.match(r'^[a-z]{2,3}$', lang)]
    
    return ','.join(valid_langs)
