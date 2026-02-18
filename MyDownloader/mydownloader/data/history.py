"""
Download History Management
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from ..constants import HISTORY_FILE, MAX_HISTORY_ENTRIES, DATA_DIR
from ..utils.logger import get_logger

logger = get_logger(__name__)


class HistoryManager:
    """Manage download history"""
    
    def __init__(self):
        self._history: List[Dict] = []
        self._ensure_data_dir()
        self.load()
    
    def _ensure_data_dir(self):
        """Ensure data directory exists"""
        os.makedirs(DATA_DIR, exist_ok=True)
    
    def load(self) -> bool:
        """Load history from file"""
        try:
            if os.path.exists(HISTORY_FILE):
                with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                    self._history = json.load(f)
                logger.info(f"Loaded {len(self._history)} history entries")
                return True
            else:
                self._history = []
        except Exception as e:
            logger.error(f"Failed to load history: {e}")
            self._history = []
        return False
    
    def save(self) -> bool:
        """Save history to file"""
        try:
            # Limit history entries
            if len(self._history) > MAX_HISTORY_ENTRIES:
                self._history = self._history[-MAX_HISTORY_ENTRIES:]
            
            with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(self._history, f, indent=4, ensure_ascii=False)
            logger.info(f"Saved {len(self._history)} history entries")
            return True
        except Exception as e:
            logger.error(f"Failed to save history: {e}")
            return False
    
    def add_entry(self, url: str, title: str, download_type: str = 'video',
                  status: str = 'completed', file_path: Optional[str] = None) -> None:
        """
        Add entry to history
        
        Args:
            url: Download URL
            title: Title of downloaded content
            download_type: Type (video, playlist, audio)
            status: Download status (completed, failed, cancelled)
            file_path: Path to downloaded file
        """
        entry = {
            'url': url,
            'title': title,
            'type': download_type,
            'status': status,
            'file_path': file_path,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self._history.append(entry)
        self.save()
        logger.info(f"Added history entry: {title}")
    
    def get_all(self) -> List[Dict]:
        """Get all history entries"""
        return self._history.copy()
    
    def get_recent(self, count: int = 10) -> List[Dict]:
        """Get recent history entries"""
        return self._history[-count:]
    
    def search(self, query: str) -> List[Dict]:
        """
        Search history
        
        Args:
            query: Search query
            
        Returns:
            Matching entries
        """
        query_lower = query.lower()
        return [
            entry for entry in self._history
            if query_lower in entry.get('title', '').lower()
            or query_lower in entry.get('url', '').lower()
        ]
    
    def clear(self) -> bool:
        """Clear all history"""
        self._history = []
        return self.save()
    
    def remove_entry(self, index: int) -> bool:
        """Remove entry by index"""
        try:
            if 0 <= index < len(self._history):
                del self._history[index]
                self.save()
                return True
        except Exception as e:
            logger.error(f"Failed to remove history entry: {e}")
        return False
    
    def get_statistics(self) -> Dict:
        """Get download statistics"""
        total = len(self._history)
        completed = sum(1 for e in self._history if e.get('status') == 'completed')
        failed = sum(1 for e in self._history if e.get('status') == 'failed')
        
        return {
            'total': total,
            'completed': completed,
            'failed': failed,
            'success_rate': (completed / total * 100) if total > 0 else 0
        }


# Global instance
history_manager = HistoryManager()
