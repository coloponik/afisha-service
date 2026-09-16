from dishka import make_async_container, AsyncContainer

from monitoring.application.providers import ConfigProvider, ServiceProvider
from monitoring.core.config import Settings
from monitoring.infrastructure.providers import PostgresProvider, KafkaProvider, QueueProvider, \
    WebSocketProvider


def create_container(settings: Settings) -> AsyncContainer:
    return make_async_container(
        ConfigProvider(settings),
        ServiceProvider(),
        PostgresProvider(),
        KafkaProvider(),
        QueueProvider(),
        WebSocketProvider()
    )
