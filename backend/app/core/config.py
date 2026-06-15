import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment variables."""

    database_url: str = os.getenv(
        "DATABASE_URL", "postgresql://propertydb:propertydb_password@localhost:5432/propsearch"
    )
    fastapi_debug: bool = os.getenv("FASTAPI_DEBUG", "false").lower() == "true"
    environment: str = os.getenv("ENVIRONMENT", "development")

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
