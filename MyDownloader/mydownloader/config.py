"""
Configuration Management
"""

import os
import json
from typing import Dict, Any
from .constants import DATA_DIR, SETTINGS_FILE, DEFAULT_SETTINGS
from .utils.logger import get_logger

logger = get_logger(__name__)


class Config:
    """Application Configuration Manager"""
    
    def __init__(self):
        self._settings = DEFAULT_SETTINGS.copy()
        self._ensure_data_dir()
        self.load()
    
    def _ensure_data_dir(self):
        """Create data directory if it doesn't exist"""
        os.makedirs(DATA_DIR, exist_ok=True)
    
    def load(self) -> bool:
        """Load settings from file"""
        try:
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    self._settings.update(loaded_settings)
                logger.info("Settings loaded successfully")
                return True
        except Exception as e:
            logger.error(f"Failed to load settings: {e}")
        return False
    
    def save(self) -> bool:
        """Save settings to file"""
        try:
            with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, indent=4, ensure_ascii=False)
            logger.info("Settings saved successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value"""
        return self._settings.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a setting value"""
        self._settings[key] = value
    
    def update(self, settings: Dict[str, Any]) -> None:
        """Update multiple settings"""
        self._settings.update(settings)
    
    def reset(self) -> None:
        """Reset to default settings"""
        self._settings = DEFAULT_SETTINGS.copy()
        logger.info("Settings reset to defaults")
    
    def get_all(self) -> Dict[str, Any]:
        """Get all settings"""
        return self._settings.copy()
    
    @property
    def download_folder(self) -> str:
        return self.get('download_folder')
    
    @download_folder.setter
    def download_folder(self, value: str):
        self.set('download_folder', value)
    
    @property
    def audio_format(self) -> str:
        return self.get('audio_format')
    
    @audio_format.setter
    def audio_format(self, value: str):
        self.set('audio_format', value)
    
    @property
    def theme(self) -> str:
        return self.get('theme')
    
    @theme.setter
    def theme(self, value: str):
        self.set('theme', value)


# Global config instance
config = Config()
