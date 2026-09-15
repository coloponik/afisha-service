from collections.abc import AsyncIterator

from dishka import Provider, provide, Scope
from faststream.kafka import KafkaBroker

from monitoring.core.config import PostgresConfig, KafkaConfig
from monitoring.infrastructure.kafka.consumer import create_kafka_broker
from monitoring.infrastructure.postgres.manager import PostgresClient, DatabaseManager


class KafkaProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_kafka_broker(self, config: KafkaConfig) -> KafkaBroker:
        return create_kafka_broker(config)


class PostgresProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_postgres(self, config: PostgresConfig) -> AsyncIterator[PostgresClient]:
        postgres = PostgresClient(config)

        yield postgres

        await postgres.close()

    @provide(scope=Scope.REQUEST)
    async def get_db(self, postgres: PostgresClient) -> AsyncIterator[DatabaseManager]:
        async with postgres.session() as db:
            yield db
