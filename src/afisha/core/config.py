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
    timeout: float = 3.0


class ProtectionApiConfig(BaseModel):
    base_url: str
    timeout: float = 3.0


class ConnectorsConfig(BaseModel):
    payment: PaymentApiConfig
    protection: ProtectionApiConfig


class BookingConfig(BaseModel):
    ttl_minutes: int


class Settings(BaseSettings):
    app: AppConfig
    project: ProjectConfig
    postgres: PostgresConfig
    connectors: ConnectorsConfig
    booking: BookingConfig

    model_config = SettingsConfigDict(
        env_file=".env.dev",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )
