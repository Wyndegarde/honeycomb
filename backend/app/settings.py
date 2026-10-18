from __future__ import annotations

import logging
import os
from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.constants import POSTGRES_PORT, AppEnv

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(extra="ignore", case_sensitive=False)

    # Logging configuration
    log_level: str = "INFO"

    # Database Configuration
    db_host: str | None = "localhost"
    db_port: int | None = POSTGRES_PORT
    db_username: str | None = None
    db_password: SecretStr = Field(default=SecretStr("password"))
    db_name: str | None = None


def get_app_env() -> AppEnv:
    """Get the application environment from the APP_ENV environment variable."""
    env_str = os.getenv("APP_ENV", "DEV")
    return AppEnv.from_str(env_str)


def _resolve_env_file(env: AppEnv) -> str | None:
    """
    Return the existing env_file for the given environment (e.g., .env.test),
    fall back to .env if present, otherwise return None.

    """
    env_file_map = {
        AppEnv.DEV: ".env.dev",
        AppEnv.TEST: ".env.test",
    }

    env_file_name = env_file_map.get(env)

    if env_file_name and Path(env_file_name).exists():
        return env_file_name

    if Path(".env").exists():
        logger.warning(
            f"{env_file_name!r} not found for env={env}. Falling back to '.env'"
        )
        return ".env"

    logger.warning(
        f"No env file found for env={env}. Tried {env_file_name!r} and '.env'. "
    )
    return None


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Get application settings."""

    app_env = get_app_env()
    env_file = _resolve_env_file(app_env)

    if env_file:
        logger.info(f"Loading settings using env file: {env_file}")
        return Settings(_env_file=env_file)  # type: ignore - pyright not recognising methods from parent class. investigate

    return Settings()
