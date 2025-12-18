# config/settings.py
import json
from pathlib import Path
from typing import Any

class Settings:
    _instance = None
    _config_file = Path.home() / '.archive_manager' / 'config.json'
    
    DEFAULT_SETTINGS = {
        'database': {
            'type': 'sqlite',
            'path': str(Path.home() / '.archive_manager' / 'archives.db')
        },
        'storage': {
            'base_path': str(Path.home() / 'Archives')
        },
        'ui': {
            'theme': 'light',
            'language': 'fr'
        },
        'permissions': {
            'allow_file_deletion': True,
            'allow_folder_deletion': True,
            'require_confirmation': True
        }
    }
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_settings()
        return cls._instance
    
    def _load_settings(self):
        """Load settings from file or create default"""
        if self._config_file.exists():
            with open(self._config_file, 'r', encoding='utf-8') as f:
                self.settings = json.load(f)
        else:
            self.settings = self.DEFAULT_SETTINGS.copy()
            self.save()
    
    def save(self):
        """Save settings to file"""
        self._config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self._config_file, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, indent=4, ensure_ascii=False)
    
    def get(self, key: str, default=None) -> Any:
        """Get setting value by key (supports dot notation)"""
        keys = key.split('.')
        value = self.settings
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default
    
    def set(self, key: str, value: Any):
        """Set setting value by key (supports dot notation)"""
        keys = key.split('.')
        settings = self.settings
        for k in keys[:-1]:
            if k not in settings:
                settings[k] = {}
            settings = settings[k]
        settings[keys[-1]] = value
        self.save()
    
    def __getitem__(self, key: str) -> Any:
        """Allow dictionary-like access"""
        return self.get(key)
    
    def __setitem__(self, key: str, value: Any):
        """Allow dictionary-like assignment"""
        self.set(key, value)