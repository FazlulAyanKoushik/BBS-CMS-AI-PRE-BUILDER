"""Centralized configuration settings for BBS-CMS AI Pre-Builder.

All environment variables and default settings are defined here.
Uses Pydantic Settings for validation and type safety.
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=None,  # Don't auto-load .env; call load_dotenv() explicitly in entrypoints
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_name: str = "BBS-CMS AI Pre-Builder"
    app_version: str = "0.1.0"
    debug: bool = False

    # Server
    host: str = "127.0.0.1"
    port: int = 8000
    reload: bool = True

    # LLM Provider
    llm_provider: str = "mock"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-3.6-flash"

    # CSV Processing
    max_csv_bytes: int = 10 * 1024 * 1024  # 10 MB
    supported_encodings: list[str] = [
        "utf-8-sig",
        "utf-8",
        "cp932",
        "shift_jis",
        "latin-1",
    ]

    # Contract
    contract_version: str = "1.0.0"

    # Logging
    log_level: str = "INFO"

    @property
    def is_gemini_enabled(self) -> bool:
        """Check if Gemini provider is properly configured."""
        return self.llm_provider == "gemini" and bool(self.gemini_api_key)


# Global settings holder
class _SettingsHolder:
    def __init__(self):
        self._settings: Settings | None = None

    def get(self) -> Settings:
        if self._settings is None:
            self._settings = Settings()
        return self._settings

    def reload(self) -> Settings:
        self._settings = Settings()
        return self._settings


_holder = _SettingsHolder()


def get_settings() -> Settings:
    """Get settings instance (creates new if not exists)."""
    return _holder.get()


def reload_settings() -> Settings:
    """Force reload settings from environment (useful for tests)."""
    return _holder.reload()


# Global settings instance - proxy to holder
class _SettingsProxy:
    def __getattr__(self, name):
        return getattr(_holder.get(), name)

    def __setattr__(self, name, value):
        if name == "_holder":
            super().__setattr__(name, value)
        else:
            setattr(_holder.get(), name, value)


settings = _SettingsProxy()