from __future__ import annotations

import os
from functools import cached_property

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Required
    SUPABASE_URL: str
    SUPABASE_KEY: str

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:5173"

    # OpenAI (optional — AI endpoints return 503 if missing)
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL_VISION: str = "gpt-4o"

    # Server
    PORT: int = 8000

    @cached_property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    @cached_property
    def openai_client(self):
        if not self.OPENAI_API_KEY:
            return None
        from openai import AsyncOpenAI

        return AsyncOpenAI(api_key=self.OPENAI_API_KEY)


def get_settings() -> Settings:
    return Settings()
