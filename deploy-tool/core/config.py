"""Configuration management for the deploy tool."""

import os
import json
from typing import Dict, Any, Optional


class ConfigManager:
    def __init__(self, config_file: str = '.deploy-config.json'):
        self.config_file = config_file
        self._config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_config(self) -> None:
        """Save configuration to file."""
        with open(self.config_file, 'w') as f:
            json.dump(self._config, f, indent=2)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        keys = key.split('.')
        config = self._config
        
        for k in keys:
            if isinstance(config, dict) and k in config:
                config = config[k]
            else:
                return default
        return config
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self.save_config()
    
    def update(self, updates: Dict[str, Any]) -> None:
        """Update configuration with dictionary."""
        self._config.update(updates)
        self.save_config()
    
    @property
    def config(self) -> Dict[str, Any]:
        """Get full configuration."""
        return self._config
    
    @config.setter
    def config(self, value: Dict[str, Any]) -> None:
        """Set full configuration."""
        self._config = value
        self.save_config()
 
