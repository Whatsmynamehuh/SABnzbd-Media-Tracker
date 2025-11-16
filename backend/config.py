import yaml
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel


class SABnzbdConfig(BaseModel):
    url: str
    api_key: str


class ArrInstanceConfig(BaseModel):
    name: str
    url: str
    api_key: str


class ServerConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 3001


class CleanupConfig(BaseModel):
    completed_after_hours: int = 48
    check_interval_minutes: int = 60


class Config(BaseModel):
    sabnzbd: SABnzbdConfig
    radarr: List[ArrInstanceConfig] = []
    sonarr: List[ArrInstanceConfig] = []
    server: ServerConfig = ServerConfig()
    cleanup: CleanupConfig = CleanupConfig()


def load_config(config_path: str = "config.yml") -> Config:
    """Load configuration from YAML file."""
    path = Path(config_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Config file not found: {config_path}\n"
            "Please copy config.example.yml to config.yml and configure it."
        )

    with open(path, 'r') as f:
        data = yaml.safe_load(f)

    return Config(**data)


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global config instance."""
    global _config
    if _config is None:
        _config = load_config()
    return _config
