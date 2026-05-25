from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../../infra/.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = (
        "postgresql+asyncpg://packing:packing_dev@postgres:5432/packing_report"
    )
    secret_key: str = "change-me-to-a-random-secret-in-production"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    odds_api_key: str = ""
    odds_api_base_url: str = "https://api.the-odds-api.com/v4"
    cors_origins: list[str] = ["http://localhost:3000"]
    redis_url: str = "redis://redis:6379/0"
    ingestion_interval_minutes: int = 15


settings = Settings()
