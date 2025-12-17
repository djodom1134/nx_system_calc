"""Application configuration."""

import json
import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List

from pydantic import Field
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings."""

    # API Settings
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    api_reload: bool = Field(default=True, env="API_RELOAD")

    # Security
    secret_key: str = Field(default="change-me-in-production", env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    # Database
    database_url: str = Field(default="sqlite:///./nx_calculator.db", env="DATABASE_URL")

    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000"], env="CORS_ORIGINS"
    )

    # Email
    smtp_host: str = Field(default="smtp.gmail.com", env="SMTP_HOST")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_user: str = Field(default="", env="SMTP_USER")
    smtp_password: str = Field(default="", env="SMTP_PASSWORD")
    smtp_from: str = Field(default="noreply@networkoptix.com", env="SMTP_FROM")
    smtp_bcc: str = Field(default="sales@networkoptix.com", env="SMTP_BCC")

    # File Storage
    upload_dir: str = Field(default="./uploads", env="UPLOAD_DIR")
    reports_dir: str = Field(default="./reports", env="REPORTS_DIR")
    max_upload_size: int = Field(default=5242880, env="MAX_UPLOAD_SIZE")  # 5MB

    # Rate Limiting
    rate_limit_per_minute: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")

    # Feature Flags
    enable_webhooks: bool = Field(default=False, env="ENABLE_WEBHOOKS")
    enable_analytics: bool = Field(default=False, env="ENABLE_ANALYTICS")

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    # Configuration Directory
    config_dir: str = Field(default="", env="CONFIG_DIR")

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


class ConfigLoader:
    """Load and cache configuration files."""

    @classmethod
    def _get_config_dir(cls) -> Path:
        """Get the configuration directory path."""
        settings = get_settings()

        # Use environment variable if set
        if settings.config_dir:
            config_path = Path(settings.config_dir)
            logger.info(f"Using CONFIG_DIR from environment: {config_path}")
        else:
            # Default: relative path from this file
            config_path = Path(__file__).parent.parent.parent.parent / "config"
            logger.info(f"Using default config directory: {config_path}")

        # Verify the directory exists
        if not config_path.exists():
            logger.error(f"Config directory does not exist: {config_path}")
            raise FileNotFoundError(
                f"Configuration directory not found: {config_path}. "
                f"Please set CONFIG_DIR environment variable or ensure config files are deployed."
            )

        return config_path

    @classmethod
    def _load_config_file(cls, filename: str, key: str = None) -> Any:
        """Load a configuration file with error handling."""
        try:
            config_dir = cls._get_config_dir()
            file_path = config_dir / filename

            logger.debug(f"Loading config file: {file_path}")

            if not file_path.exists():
                raise FileNotFoundError(
                    f"Configuration file not found: {file_path}. "
                    f"Please ensure {filename} is deployed in the config directory."
                )

            with open(file_path) as f:
                data = json.load(f)

            if key:
                if key not in data:
                    raise KeyError(f"Key '{key}' not found in {filename}")
                return data[key]

            return data

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {filename}: {e}")
            raise ValueError(f"Invalid JSON in configuration file {filename}: {e}")
        except Exception as e:
            logger.error(f"Error loading {filename}: {e}")
            raise

    @classmethod
    @lru_cache()
    def load_resolutions(cls) -> List[Dict[str, Any]]:
        """Load resolution presets."""
        return cls._load_config_file("resolutions.json", "resolutions")

    @classmethod
    @lru_cache()
    def load_codecs(cls) -> List[Dict[str, Any]]:
        """Load codec configurations."""
        return cls._load_config_file("codecs.json", "codecs")

    @classmethod
    @lru_cache()
    def load_raid_types(cls) -> List[Dict[str, Any]]:
        """Load RAID type configurations."""
        return cls._load_config_file("raid_types.json", "raid_types")

    @classmethod
    @lru_cache()
    def load_server_specs(cls) -> Dict[str, Any]:
        """Load server specifications."""
        return cls._load_config_file("server_specs.json")

    @classmethod
    def get_codec_by_id(cls, codec_id: str) -> Dict[str, Any]:
        """Get codec configuration by ID."""
        codecs = cls.load_codecs()
        for codec in codecs:
            if codec["id"] == codec_id:
                return codec
        raise ValueError(f"Codec not found: {codec_id}")

    @classmethod
    def get_resolution_by_id(cls, resolution_id: str) -> Dict[str, Any]:
        """Get resolution configuration by ID."""
        resolutions = cls.load_resolutions()
        for resolution in resolutions:
            if resolution["id"] == resolution_id:
                return resolution
        raise ValueError(f"Resolution not found: {resolution_id}")

    @classmethod
    def get_raid_by_id(cls, raid_id: str) -> Dict[str, Any]:
        """Get RAID configuration by ID."""
        raid_types = cls.load_raid_types()
        for raid in raid_types:
            if raid["id"] == raid_id:
                return raid
        raise ValueError(f"RAID type not found: {raid_id}")

