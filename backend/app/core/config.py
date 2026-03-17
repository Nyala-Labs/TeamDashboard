"""Application configuration."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/nyala_dashboard"
    database_url_sync: str = "postgresql://postgres:postgres@localhost:5432/nyala_dashboard"

    # Auth
    secret_key: str = "change-me-in-production-use-openssl-rand-hex-32"
    access_token_expire_minutes: int = 60 * 24  # 24 hours

    # Google Calendar
    google_client_id: str = ""
    google_client_secret: str = ""
    google_calendar_credentials_path: str = "credentials.json"
    google_calendar_token_path: str = "token.json"

    # App
    app_name: str = "Nyala Labs Dashboard"
    cors_origins: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
