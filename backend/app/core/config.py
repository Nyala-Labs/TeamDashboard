"""Application configuration."""
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


def _to_asyncpg_url(url: str) -> str:
    """Convert postgres:// to postgresql+asyncpg:// for async drivers."""
    if url.startswith("postgres://"):
        return "postgresql+asyncpg://" + url[len("postgres://") :]
    if url.startswith("postgresql://") and "+asyncpg" not in url:
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


def _to_sync_url(url: str) -> str:
    """Convert postgresql+asyncpg:// to postgresql:// for Alembic/sync."""
    return url.replace("postgresql+asyncpg://", "postgresql://", 1)


class Settings(BaseSettings):
    """Application settings. DATABASE_URL from env overrides defaults (Supabase)."""

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/nyala_dashboard"
    database_url_sync: str = "postgresql://postgres:postgres@localhost:5432/nyala_dashboard"
    secret_key: str = "change-me-in-production-use-openssl-rand-hex-32"
    access_token_expire_minutes: int = 60 * 24
    google_client_id: str = ""
    google_client_secret: str = ""
    google_calendar_credentials_path: str = "credentials.json"
    google_calendar_token_path: str = "token.json"
    app_name: str = "Nyala Labs Dashboard"
    cors_origins: list[str] = ["http://localhost:3000"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}

    @field_validator("database_url", mode="before")
    @classmethod
    def _normalize_async_url(cls, v: str) -> str:
        return _to_asyncpg_url(v) if isinstance(v, str) else v

    @field_validator("database_url_sync", mode="before")
    @classmethod
    def _normalize_sync_url(cls, v: str) -> str:
        return _to_sync_url(v) if isinstance(v, str) else v


settings = Settings()
