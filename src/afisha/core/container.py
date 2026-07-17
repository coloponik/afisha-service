from dishka import make_async_container, AsyncContainer

from afisha.application.providers import ConfigProvider, ServiceProvider
from afisha.core.config import Settings
from afisha.infrastracture.providers import PostgresProvider, ConnectorsProvider


def create_container(settings: Settings) -> AsyncContainer:
    return make_async_container(
        ConfigProvider(settings),
        ServiceProvider(),
        PostgresProvider(),
        ConnectorsProvider()
    )
