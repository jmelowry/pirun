"""Configuration handling for PiRun."""
import os
import yaml
from pathlib import Path
from typing import Dict, Any


class Config:
    """Project configuration manager."""

    DEFAULT_CONFIG = {
        'name': 'pirun-project',
        'base_dir': '',
        'venv_python': '.venv/bin/python',
        'server': {
            'addr': '127.0.0.1:8080',
            'read_timeout_ms': 5000,
            'write_timeout_ms': 15000,
            'run_timeout_ms': 30000,
            'max_upload_bytes': 5_000_000
        }
    }

    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir).resolve()
        self.config_path = self.base_dir / '.pirun.yaml'
        self.config = self._load()

    def _load(self) -> Dict[str, Any]:
        """Load configuration from .pirun.yaml."""
        if not self.config_path.exists():
            return self.DEFAULT_CONFIG.copy()

        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)

        # Ensure base_dir is set correctly
        config['base_dir'] = str(self.base_dir)
        return config

    def save(self):
        """Save configuration to .pirun.yaml."""
        with open(self.config_path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)

    def get(self, key: str, default=None):
        """Get a configuration value."""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        return value

    def set(self, key: str, value: Any):
        """Set a configuration value."""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
