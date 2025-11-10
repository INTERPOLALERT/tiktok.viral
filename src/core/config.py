"""
Configuration Management System
Handles all application settings and preferences
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
import logging

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manages application configuration and settings"""

    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent
        self.config_dir = self.base_dir / "config"
        self.config_dir.mkdir(exist_ok=True)

        self.config_file = self.config_dir / "settings.json"
        self.secrets_file = self.config_dir / ".secrets.enc"
        self.key_file = self.config_dir / ".key"

        self._config = {}
        self._secrets = {}
        self._cipher = None

        self._initialize()

    def _initialize(self):
        """Initialize configuration system"""
        # Initialize encryption
        if not self.key_file.exists():
            key = Fernet.generate_key()
            self.key_file.write_bytes(key)
            self.key_file.chmod(0o600)  # Secure permissions

        key = self.key_file.read_bytes()
        self._cipher = Fernet(key)

        # Load configuration
        self._load_config()
        self._load_secrets()

        # Initialize default settings
        if not self._config:
            self._set_defaults()

    def _set_defaults(self):
        """Set default configuration values"""
        self._config = {
            "app": {
                "name": "CreatorStudio AI",
                "version": "1.0.0",
                "theme": "dark",
                "language": "en",
                "auto_save": True,
                "auto_save_interval": 300  # 5 minutes
            },
            "ai": {
                "provider": "openai",
                "model": "gpt-4-turbo-preview",
                "temperature": 0.7,
                "max_tokens": 4000,
                "timeout": 60
            },
            "video": {
                "default_resolution": "1920x1080",
                "default_fps": 30,
                "default_format": "mp4",
                "quality": "high",
                "hardware_acceleration": True
            },
            "image": {
                "default_size": "1024x1024",
                "default_format": "png",
                "quality": 95
            },
            "audio": {
                "default_format": "mp3",
                "bitrate": 320,
                "sample_rate": 44100,
                "voice_model": "neural"
            },
            "social_media": {
                "platforms": ["tiktok", "instagram", "youtube", "twitter", "facebook"],
                "auto_optimize": True,
                "schedule_enabled": True
            },
            "analytics": {
                "tracking_enabled": True,
                "refresh_interval": 3600,  # 1 hour
                "history_days": 90
            },
            "storage": {
                "cache_size_mb": 1024,
                "auto_cleanup": True,
                "compression": True
            },
            "performance": {
                "multiprocessing": True,
                "max_workers": 4,
                "gpu_enabled": True
            },
            "ui": {
                "show_tooltips": True,
                "animations": True,
                "compact_mode": False,
                "sidebar_width": 250
            }
        }
        self.save_config()

    def _load_config(self):
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
                logger.info("Configuration loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load configuration: {e}")
                self._config = {}

    def _load_secrets(self):
        """Load encrypted secrets"""
        if self.secrets_file.exists():
            try:
                encrypted_data = self.secrets_file.read_bytes()
                decrypted_data = self._cipher.decrypt(encrypted_data)
                self._secrets = json.loads(decrypted_data.decode('utf-8'))
                logger.info("Secrets loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load secrets: {e}")
                self._secrets = {}

    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2)
            logger.info("Configuration saved successfully")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")

    def save_secrets(self):
        """Save encrypted secrets"""
        try:
            data = json.dumps(self._secrets).encode('utf-8')
            encrypted_data = self._cipher.encrypt(data)
            self.secrets_file.write_bytes(encrypted_data)
            self.secrets_file.chmod(0o600)
            logger.info("Secrets saved successfully")
        except Exception as e:
            logger.error(f"Failed to save secrets: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        return value

    def set(self, key: str, value: Any):
        """Set configuration value"""
        keys = key.split('.')
        config = self._config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self.save_config()

    def get_secret(self, key: str) -> Optional[str]:
        """Get secret value"""
        return self._secrets.get(key)

    def set_secret(self, key: str, value: str):
        """Set secret value"""
        self._secrets[key] = value
        self.save_secrets()

    def get_all(self) -> Dict[str, Any]:
        """Get all configuration"""
        return self._config.copy()

    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self._config = {}
        self._set_defaults()


# Global config instance
config = ConfigManager()
