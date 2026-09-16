import os

from pydantic import BaseModel, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8104
    reload: bool = False


class PostgresConfig(BaseModel):
    host: str
    port: int
    user: str
    password: SecretStr
    database: str
    echo: bool = False

    @property
    def url(self):
        return (
            f"postgresql+psycopg://{self.user}"
            f":{self.password.get_secret_value()}"
            f"@{self.host}:{self.port}/{self.database}"
        )


class KafkaConfig(BaseModel):
    bootstrap_servers: str = "localhost:9092"
    purchase_topic: str = "tickets.purchased"
    group_id: str = "monitoring"


class Settings(BaseSettings):
    app: AppConfig
    postgres: PostgresConfig
    kafka: KafkaConfig

    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", ".env.dev"),
        env_file_encoding="utf-8",
        env_prefix="MONITORING__",
        env_nested_delimiter="__",
        extra="ignore"
    )
