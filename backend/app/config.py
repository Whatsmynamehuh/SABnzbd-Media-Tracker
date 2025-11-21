"""
Configuration management with YAML and environment variable support.
"""
import yaml
import os
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class SABnzbdConfig(BaseModel):
    """SABnzbd configuration."""
    url: str
    api_key: str


class ArrInstanceConfig(BaseModel):
    """Radarr/Sonarr instance configuration."""
    name: str
    url: str
    api_key: str
    category: Optional[str] = None


class ServerConfig(BaseModel):
    """Server configuration."""
    host: str = "0.0.0.0"
    port: int = 3001


class CleanupConfig(BaseModel):
    """Cleanup configuration."""
    completed_after_hours: int = 48
    check_interval_minutes: int = 60


class DebugConfig(BaseModel):
    """Debug logging configuration."""
    enable_priority_logging: bool = False
    enable_category_logging: bool = False
    enable_poster_logging: bool = False
    enable_parsing_logging: bool = False
    enable_match_logging: bool = False


class Config(BaseModel):
    """Main application configuration."""
    sabnzbd: SABnzbdConfig
    radarr: List[ArrInstanceConfig] = []
    sonarr: List[ArrInstanceConfig] = []
    server: ServerConfig = ServerConfig()
    cleanup: CleanupConfig = CleanupConfig()
    debug: DebugConfig = DebugConfig()


def load_config(config_path: str = "config.yml") -> Config:
    """
    Load configuration from YAML file.

    Args:
        config_path: Path to config YAML file

    Returns:
        Config object

    Raises:
        FileNotFoundError: If config file doesn't exist
    """
    path = Path(config_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Config file not found: {config_path}\n"
            "Please copy config.example.yml to config.yml and configure it."
        )

    with open(path, 'r') as f:
        data = yaml.safe_load(f)

    # Allow environment variable overrides for sensitive data
    if os.getenv("SABNZBD_URL"):
        data['sabnzbd']['url'] = os.getenv("SABNZBD_URL")
    if os.getenv("SABNZBD_API_KEY"):
        data['sabnzbd']['api_key'] = os.getenv("SABNZBD_API_KEY")

    return Config(**data)


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global config instance."""
    global _config
    if _config is None:
        _config = load_config()
    return _config
