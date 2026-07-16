from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str
    ENV: str
    DEBUG: bool
    DATABASE_URL: str
    PAYMENT_API_URL: str
    PROTECTION_API_URL: str
    BOOKING_TTL_MINUTES: int

    model_config = SettingsConfigDict(
        env_file=".env.dev",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )