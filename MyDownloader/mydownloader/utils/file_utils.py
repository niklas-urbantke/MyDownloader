"""
File Utilities
"""

import os
import re
from typing import Optional
from .logger import get_logger

logger = get_logger(__name__)


def clean_filename(filename: str) -> str:
    """
    Remove invalid characters from filename
    
    Args:
        filename: Original filename
        
    Returns:
        Cleaned filename safe for Windows/Unix
    """
    # Remove invalid characters
    cleaned = re.sub(r'[<>:"/\\|?*]', '', filename)
    
    # Remove control characters
    cleaned = re.sub(r'[\x00-\x1f\x7f]', '', cleaned)
    
    # Trim whitespace
    cleaned = cleaned.strip()
    
    # Replace multiple spaces with single space
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    # Limit length (Windows max path is 260, leave room for path)
    max_filename_length = 200
    if len(cleaned) > max_filename_length:
        name, ext = os.path.splitext(cleaned)
        name = name[:max_filename_length - len(ext)]
        cleaned = name + ext
    
    return cleaned


def ensure_directory(path: str) -> bool:
    """
    Ensure directory exists, create if necessary
    
    Args:
        path: Directory path
        
    Returns:
        True if directory exists or was created successfully
    """
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Failed to create directory {path}: {e}")
        return False


def get_file_size(filepath: str) -> Optional[int]:
    """
    Get file size in bytes
    
    Args:
        filepath: Path to file
        
    Returns:
        File size in bytes or None if error
    """
    try:
        return os.path.getsize(filepath)
    except Exception as e:
        logger.error(f"Failed to get file size for {filepath}: {e}")
        return None


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def get_safe_path(base_dir: str, filename: str) -> str:
    """
    Get safe file path, ensuring it's within base directory
    
    Args:
        base_dir: Base directory
        filename: Filename
        
    Returns:
        Safe full path
    """
    # Clean filename
    filename = clean_filename(filename)
    
    # Join paths
    full_path = os.path.join(base_dir, filename)
    
    # Resolve to absolute path
    full_path = os.path.abspath(full_path)
    base_dir = os.path.abspath(base_dir)
    
    # Ensure path is within base directory (prevent directory traversal)
    if not full_path.startswith(base_dir):
        logger.warning(f"Attempted directory traversal: {full_path}")
        return os.path.join(base_dir, os.path.basename(filename))
    
    return full_path


def file_exists(filepath: str) -> bool:
    """Check if file exists and is a file"""
    return os.path.isfile(filepath)


def directory_exists(dirpath: str) -> bool:
    """Check if directory exists and is a directory"""
    return os.path.isdir(dirpath)
