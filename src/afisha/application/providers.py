from dishka import Provider, provide, Scope

from afisha.core.config import Settings, AppConfig, ProjectConfig, PostgresConfig, \
    ConnectorsConfig, BookingConfig


class ConfigProvider(Provider):
    def __init__(self, settings: Settings):
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
    pass
