from dishka import make_async_container, AsyncContainer

from monitoring.application.providers import ConfigProvider, ServiceProvider
from monitoring.core.config import Settings


def create_container(settings: Settings) -> AsyncContainer:
    return make_async_container(
        ConfigProvider(settings),
        ServiceProvider()
    )
