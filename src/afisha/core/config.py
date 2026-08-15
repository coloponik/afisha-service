import os

from pydantic import BaseModel, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseModel):
    host: str
    port: int
    reload: bool


class PostgresConfig(BaseModel):
    host: str
    port: int
    user: str
    password: SecretStr
    database: str
    echo: bool = False
    pool_size: int = 10
    max_overflow: int = 20

    @property
    def url(self) -> str:
        return (
            f"postgresql+psycopg://{self.user}"
            f":{self.password.get_secret_value()}"
            f"@{self.host}:{self.port}/{self.database}"
        )


class ProjectConfig(BaseModel):
    name: str
    env: str


class PaymentApiConfig(BaseModel):
    base_url: str
    timeout: float = 1.0
    rate_limit_requests: int | None = 5
    rate_limit_interval: int | None = 1


class ProtectionApiConfig(BaseModel):
    base_url: str
    timeout: float = 2.0
    rate_limit_requests: int | None = None
    rate_limit_interval: int | None = None


class RedisConfig(BaseModel):
    host: str
    port: int
    password: SecretStr | None = None
    database: int = 0

    @property
    def url(self) -> str:
        if self.password is None:
            return f"redis://{self.host}:{self.port}/{self.database}"

        password = self.password.get_secret_value()
        return f"redis://:{password}@{self.host}:{self.port}/{self.database}"


class ConnectorsConfig(BaseModel):
    payment: PaymentApiConfig
    protection: ProtectionApiConfig


class BookingConfig(BaseModel):
    booking_ttl_minutes: int = 15


class Settings(BaseSettings):
    app: AppConfig
    project: ProjectConfig
    postgres: PostgresConfig
    redis: RedisConfig
    connectors: ConnectorsConfig
    booking: BookingConfig

    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", ".env.dev"),
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )
