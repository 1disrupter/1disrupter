# -*- coding: utf-8 -*-
"""Application configuration loaded from environment."""
import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


_BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.path.join(_BACKEND_DIR, ".env"),
        extra="ignore",
    )

    APP_NAME: str = "Vibe2Nite"
    APP_TAGLINE: str = "Find the vibe. Go tonight."
    DATABASE_URL: str  # required, no default so misconfig fails fast

    # Brand palette (hex) — exposed to templates so docs/admin stay in sync.
    BRAND_PRIMARY: str = "#A260FF"       # Neon Purple
    BRAND_DEEP: str = "#8A49FF"          # Electric Violet
    BRAND_PINK: str = "#FF3BA7"          # Electric Pink / Magenta
    BRAND_LAVENDER: str = "#C9B6FF"      # Soft Lavender
    BRAND_TEAL: str = "#40E0FF"          # Teal / Aqua glow
    BRAND_AMBER: str = "#FFB347"         # Warm Amber (busy/packed)
    BRAND_BG: str = "#05020D"            # Deep Midnight
    BRAND_CARD: str = "#11071F"          # Card background
    BRAND_BORDER: str = "#2A1846"        # Subtle border


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
