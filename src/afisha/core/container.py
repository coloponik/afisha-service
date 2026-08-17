from dishka import AsyncContainer, make_async_container

from afisha.application.providers import ConfigProvider, ServiceProvider
from afisha.core.config import Settings
from afisha.infrastracture.providers import (
    ConnectorsProvider,
    PostgresProvider,
    RedisProvider,
    CacheProvider,
    PostgresEventQueueProvider
)


def create_container(settings: Settings) -> AsyncContainer:
    return make_async_container(
        ConfigProvider(settings),
        ServiceProvider(),
        PostgresProvider(),
        RedisProvider(),
        CacheProvider(),
        PostgresEventQueueProvider(),
        ConnectorsProvider()
    )
