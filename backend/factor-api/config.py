"""Validated environment-backed configuration for the factor service."""
from __future__ import annotations

from pathlib import Path

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    host: str = Field(default="0.0.0.0", validation_alias=AliasChoices("FACTOR_API_HOST", "HOST"))
    port: int = Field(default=8000, ge=1, le=65535, validation_alias=AliasChoices("FACTOR_API_PORT", "PORT"))
    log_level: str = Field(default="INFO", validation_alias=AliasChoices("FACTOR_API_LOG_LEVEL", "LOG_LEVEL"))
    registry_path: Path = Field(
        default=BASE_DIR / "factors.json",
        validation_alias=AliasChoices("FACTOR_REGISTRY_PATH"),
    )
    year: int = Field(default=2026, ge=1900, le=2100, validation_alias=AliasChoices("FACTOR_YEAR"))
    source: str = Field(
        default="UK Government GHG Conversion Factors 2026 — revised July 2026 flat file",
        validation_alias=AliasChoices("FACTOR_SOURCE"),
    )

    @field_validator("log_level")
    @classmethod
    def normalize_log_level(cls, value: str) -> str:
        value = value.upper().strip()
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if value not in allowed:
            raise ValueError(f"Unsupported log level: {value}")
        return value


settings = Settings()
