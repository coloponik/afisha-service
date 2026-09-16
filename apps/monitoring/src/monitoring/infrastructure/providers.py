from collections.abc import AsyncIterator

from dishka import Provider, provide, Scope, AsyncContainer
from faststream.kafka import KafkaBroker

from monitoring.core.config import PostgresConfig, KafkaConfig
from monitoring.infrastructure.kafka.consumer import create_kafka_broker
from monitoring.infrastructure.postgres.manager import PostgresClient, DatabaseManager
from monitoring.infrastructure.queues.purchase_aggregates import PurchaseAggregatesQueue
from monitoring.infrastructure.websocket.manager import WebsocketManager


class KafkaProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_kafka_broker(
            self,
            config: KafkaConfig,
            container: AsyncContainer
    ) -> KafkaBroker:
        return create_kafka_broker(config, container)


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


class QueueProvider(Provider):
    @provide(scope=Scope.APP)
    def get_purchase_aggregates_queue(self) -> PurchaseAggregatesQueue:
        return PurchaseAggregatesQueue()


class WebSocketProvider(Provider):
    @provide(scope=Scope.APP)
    def get_websocket_manager(self) -> WebsocketManager:
        return WebsocketManager()
