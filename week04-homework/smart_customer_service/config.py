"""
Configuration management with hot reload support
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)


class Config:
    """Configuration manager with hot reload"""

    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self._config: Dict[str, Any] = {}
        self._last_mtime: Optional[float] = None
        self.load_config()

    def load_config(self):
        """Load configuration from file and environment"""
        # Load from .env first
        load_dotenv()

        # Default configuration
        self._config = {
            "llm": {
                "api_key": os.getenv("OPENAI_API_KEY"),
                "base_url": os.getenv("OPENAI_API_BASE"),
                "model": os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                "temperature": float(os.getenv("TEMPERATURE", "0.7"))
            },
            "server": {
                "host": os.getenv("HOST", "0.0.0.0"),
                "port": int(os.getenv("PORT", "8000"))
            },
            "plugins": {
                "enabled": True,
                "directory": "smart_customer_service/plugins",
                "auto_reload": True
            }
        }

        # Load from config file if exists
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    file_config = json.load(f)
                    self._config.update(file_config)
                self._last_mtime = self.config_file.stat().st_mtime
                logger.info(f"Loaded configuration from {self.config_file}")
            except Exception as e:
                logger.error(f"Error loading config file: {e}")

    def reload_if_changed(self) -> bool:
        """
        Check if config file has changed and reload if necessary

        Returns:
            bool: True if config was reloaded
        """
        if not self.config_file.exists():
            return False

        current_mtime = self.config_file.stat().st_mtime
        if self._last_mtime is None or current_mtime > self._last_mtime:
            logger.info("Config file changed, reloading...")
            self.load_config()
            return True

        return False

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot-notation key"""
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
        """Set configuration value by dot-notation key"""
        keys = key.split('.')
        config = self._config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    def save(self):
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self._config, f, indent=2)
            self._last_mtime = self.config_file.stat().st_mtime
            logger.info(f"Saved configuration to {self.config_file}")
        except Exception as e:
            logger.error(f"Error saving config: {e}")

    def to_dict(self) -> Dict[str, Any]:
        """Get full configuration as dictionary"""
        return self._config.copy()


# Global config instance
config = Config()
