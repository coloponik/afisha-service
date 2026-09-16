from dishka import Provider, provide, Scope

from monitoring.core.config import Settings, AppConfig, PostgresConfig, KafkaConfig
from monitoring.infrastructure.postgres.manager import DatabaseManager
from monitoring.infrastructure.queues.purchase_aggregates import PurchaseAggregatesQueue
from monitoring.infrastructure.websocket.manager import WebsocketManager
from monitoring.services.purchase_aggregation import PurchaseAggregationService
from monitoring.services.websocket_purchase_broadcaster import WebSocketPurchaseBroadcaster


class ConfigProvider(Provider):
    def __init__(self, settings: Settings) -> None:
        super().__init__()
        self._settings = settings

    @provide(scope=Scope.APP)
    def get_settings(self) -> Settings:
        return self._settings

    @provide(scope=Scope.APP)
    def get_app_config(self) -> AppConfig:
        return self._settings.app

    @provide(scope=Scope.APP)
    def get_postgres_config(self) -> PostgresConfig:
        return self._settings.postgres

    @provide(scope=Scope.APP)
    def get_kafka_config(self) -> KafkaConfig:
        return self._settings.kafka


class ServiceProvider(Provider):
    @provide(scope=Scope.APP)
    def get_websocket_purchase_broadcaster(
            self,
            ws_manager: WebsocketManager,
            queue: PurchaseAggregatesQueue
    ) -> WebSocketPurchaseBroadcaster:
        return WebSocketPurchaseBroadcaster(
            ws_manager=ws_manager,
            queue=queue,
        )

    @provide(scope=Scope.REQUEST)
    def get_purchase_aggregation_service(
            self,
            db: DatabaseManager
    ) -> PurchaseAggregationService:
        return PurchaseAggregationService(
            db=db
        )

