from datetime import timedelta

from dishka import Provider, Scope, provide

from afisha.core.config import (
    AppConfig,
    BookingConfig,
    ConnectorsConfig,
    PostgresConfig,
    ProjectConfig,
    Settings,
)
from afisha.infrastracture.api_connectors.internal.payment import PaymentConnector
from afisha.infrastracture.api_connectors.internal.protection import ProtectionConnector
from afisha.infrastracture.postgres.manager import DatabaseManager
from afisha.services.booking import BookingService
from afisha.services.event_analytics import EventAnalyticsService


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
    def get_project_config(self) -> ProjectConfig:
        return self._settings.project

    @provide(scope=Scope.APP)
    def get_postgres_config(self) -> PostgresConfig:
        return self._settings.postgres

    @provide(scope=Scope.APP)
    def get_connectors_config(self) -> ConnectorsConfig:
        return self._settings.connectors

    @provide(scope=Scope.APP)
    def get_booking_config(self) -> BookingConfig:
        return self._settings.booking


class ServiceProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_event_analytics_service(
            self,
            db: DatabaseManager
    ) -> EventAnalyticsService:
        return EventAnalyticsService(
            db=db
        )

    @provide(scope=Scope.REQUEST)
    def get_booking_service(
            self,
            db: DatabaseManager,
            payment_connector: PaymentConnector,
            protection_connector: ProtectionConnector,
            config: BookingConfig
    ) -> BookingService:
        return BookingService(
            db=db,
            payment_connector=payment_connector,
            protection_connector=protection_connector,
            booking_ttl=timedelta(minutes=config.booking_ttl_minutes)
        )
