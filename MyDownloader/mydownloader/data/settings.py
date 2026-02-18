"""
Settings Management (Extended Config Wrapper)
"""

from typing import Dict, Any
from ..config import config
from ..utils.logger import get_logger

logger = get_logger(__name__)


class SettingsManager:
    """Extended settings management with validation"""
    
    def __init__(self):
        self.config = config
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get setting value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any, save: bool = True) -> bool:
        """
        Set setting value
        
        Args:
            key: Setting key
            value: Setting value
            save: Whether to save immediately
            
        Returns:
            True if successful
        """
        try:
            self.config.set(key, value)
            if save:
                return self.config.save()
            return True
        except Exception as e:
            logger.error(f"Failed to set setting {key}: {e}")
            return False
    
    def update(self, settings: Dict[str, Any], save: bool = True) -> bool:
        """
        Update multiple settings
        
        Args:
            settings: Dict of settings to update
            save: Whether to save immediately
            
        Returns:
            True if successful
        """
        try:
            self.config.update(settings)
            if save:
                return self.config.save()
            return True
        except Exception as e:
            logger.error(f"Failed to update settings: {e}")
            return False
    
    def reset(self, save: bool = True) -> bool:
        """
        Reset to default settings
        
        Args:
            save: Whether to save immediately
            
        Returns:
            True if successful
        """
        try:
            self.config.reset()
            if save:
                return self.config.save()
            return True
        except Exception as e:
            logger.error(f"Failed to reset settings: {e}")
            return False
    
    def get_all(self) -> Dict[str, Any]:
        """Get all settings"""
        return self.config.get_all()
    
    def export_settings(self, filepath: str) -> bool:
        """
        Export settings to file
        
        Args:
            filepath: Export file path
            
        Returns:
            True if successful
        """
        import json
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.config.get_all(), f, indent=4, ensure_ascii=False)
            logger.info(f"Settings exported to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to export settings: {e}")
            return False
    
    def import_settings(self, filepath: str, save: bool = True) -> bool:
        """
        Import settings from file
        
        Args:
            filepath: Import file path
            save: Whether to save after import
            
        Returns:
            True if successful
        """
        import json
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            self.config.update(settings)
            if save:
                self.config.save()
            logger.info(f"Settings imported from {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to import settings: {e}")
            return False
    
    # Convenience properties
    @property
    def download_folder(self) -> str:
        return self.config.download_folder
    
    @download_folder.setter
    def download_folder(self, value: str):
        self.config.download_folder = value
        self.config.save()
    
    @property
    def audio_format(self) -> str:
        return self.config.audio_format
    
    @audio_format.setter
    def audio_format(self, value: str):
        self.config.audio_format = value
        self.config.save()
    
    @property
    def theme(self) -> str:
        return self.config.theme
    
    @theme.setter
    def theme(self, value: str):
        self.config.theme = value
        self.config.save()


# Global instance
settings_manager = SettingsManager()
