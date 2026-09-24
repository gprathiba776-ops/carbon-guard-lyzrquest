"""Validated environment-backed configuration for the calculator service."""
from __future__ import annotations

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    host: str = Field(default="0.0.0.0", validation_alias=AliasChoices("CALCULATOR_API_HOST", "HOST"))
    port: int = Field(default=8000, ge=1, le=65535, validation_alias=AliasChoices("CALCULATOR_API_PORT", "PORT"))
    log_level: str = Field(default="INFO", validation_alias=AliasChoices("CALCULATOR_API_LOG_LEVEL", "LOG_LEVEL"))

    @field_validator("log_level")
    @classmethod
    def normalize_log_level(cls, value: str) -> str:
        value = value.upper().strip()
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if value not in allowed:
            raise ValueError(f"Unsupported log level: {value}")
        return value


settings = Settings()
