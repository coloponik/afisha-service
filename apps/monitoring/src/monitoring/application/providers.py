from dishka import Provider, provide, Scope

from monitoring.core.config import Settings, AppConfig, PostgresConfig, KafkaConfig
from monitoring.services.purchase_aggregation import PurchaseAggregationService


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
    def get_purchase_aggregation_service(self) -> PurchaseAggregationService:
        return PurchaseAggregationService()
