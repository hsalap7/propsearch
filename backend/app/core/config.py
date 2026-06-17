import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment variables."""

    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://propertydb:propertydb_password@localhost:5432/propsearch",
    )
    secret_key: str = os.getenv("SECRET_KEY", "your-super-secret-32-byte-key-here-123!")
    fastapi_debug: bool = os.getenv("FASTAPI_DEBUG", "false").lower() == "true"
    environment: str = os.getenv("ENVIRONMENT", "development")
    google_geocoding_api_key: str | None = os.getenv("GOOGLE_GEOCODING_API_KEY")
    nominatim_user_agent: str = os.getenv(
        "NOMINATIM_USER_AGENT", "propsearch-ingestion/1.0"
    )
    collector_headless: bool = os.getenv("COLLECTOR_HEADLESS", "true").lower() == "true"
    collector_search_urls: str = os.getenv("COLLECTOR_SEARCH_URLS", "")

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
