from datetime import timedelta

from dishka import Provider, Scope, provide

from afisha.core.config import (
    AppConfig,
    BookingConfig,
    ConnectorsConfig,
    PostgresConfig,
    ProjectConfig,
    Settings, RedisConfig, ReportConfig,
)
from afisha.infrastructure.api_connectors.internal.payment import PaymentConnector
from afisha.infrastructure.api_connectors.internal.protection import ProtectionConnector
from afisha.infrastructure.postgres.manager import DatabaseManager
from afisha.infrastructure.postgres.queue import PostgresEventQueue
from afisha.infrastructure.redis.cache_repo import CacheRepo
from afisha.infrastructure.tasks.publisher import TaskPublisher
from afisha.services.booking import BookingService
from afisha.services.event import EventService
from afisha.services.event_analytics import EventAnalyticsService
from afisha.services.report import ReportService


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
    def get_redis_config(self) -> RedisConfig:
        return self._settings.redis

    @provide(scope=Scope.APP)
    def get_report_config(self) -> ReportConfig:
        return self._settings.report

    @provide(scope=Scope.APP)
    def get_connectors_config(self) -> ConnectorsConfig:
        return self._settings.connectors

    @provide(scope=Scope.APP)
    def get_booking_config(self) -> BookingConfig:
        return self._settings.booking


class ServiceProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_event_service(
            self,
            db: DatabaseManager,
            cache: CacheRepo,
            queue: PostgresEventQueue
    ) -> EventService:
        return EventService(
            db=db,
            cache=cache,
            queue=queue
        )

    @provide(scope=Scope.REQUEST)
    def get_event_analytics_service(
            self,
            db: DatabaseManager,
            task_publisher: TaskPublisher
    ) -> EventAnalyticsService:
        return EventAnalyticsService(
            db=db,
            task_publisher=task_publisher
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

    @provide(scope=Scope.REQUEST)
    def get_report_service(
            self,
            db: DatabaseManager,
            config: ReportConfig
    ) -> ReportService:
        return ReportService(
            db=db,
            storage_path=config.storage_path
        )
