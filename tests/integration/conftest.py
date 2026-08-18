from collections.abc import AsyncGenerator

import httpx
import pytest
from asgi_lifespan import LifespanManager
from dishka import AsyncContainer, Scope, make_async_container
from fastapi import FastAPI
from sqlalchemy import text

from afisha.application.app import create_fastapi_app
from afisha.application.providers import ConfigProvider, ServiceProvider
from afisha.core.config import Settings
from afisha.infrastracture.postgres.manager import PostgresClient, DatabaseManager
from afisha.infrastracture.postgres.queue import PostgresEventQueue
from afisha.infrastracture.providers import (
    PostgresProvider,
    RedisProvider,
    CacheProvider,
    PostgresEventQueueProvider
)
from afisha.services.event import EventService
from tests.integration.mock_providers import MockConnectorsProvider


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    return Settings()


def make_test_container(settings: Settings) -> AsyncContainer:
    return make_async_container(
        ConfigProvider(settings),
        ServiceProvider(),
        PostgresProvider(),
        RedisProvider(),
        CacheProvider(),
        PostgresEventQueueProvider(),
        MockConnectorsProvider()
    )


@pytest.fixture
async def test_container(
        test_settings: Settings
) -> AsyncGenerator[AsyncContainer, None]:
    container = make_test_container(test_settings)
    yield container
    await container.close()


@pytest.fixture
async def test_app(
        test_settings: Settings,
        test_container: AsyncContainer
) -> FastAPI:
    app = create_fastapi_app(test_settings, test_container)
    return app


@pytest.fixture
async def async_client(
        test_app: FastAPI
) -> AsyncGenerator[httpx.AsyncClient, None]:
    async with LifespanManager(test_app):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=test_app),
            base_url="http://test"
        ) as client:
            yield client


@pytest.fixture
async def db(
    test_container: AsyncContainer,
) -> AsyncGenerator[DatabaseManager, None]:
    async with test_container() as request_container:
        yield await request_container.get(DatabaseManager)


@pytest.fixture(autouse=True)
async def clean_database(
        test_container: AsyncContainer
) -> AsyncGenerator[None, None]:
    yield

    async with test_container(scope=Scope.REQUEST) as req_container:
        postgres = await req_container.get(PostgresClient)

        async with postgres.engine.begin() as conn:
            await conn.execute(
                text("""
                    TRUNCATE
                        event_seats,
                        bookings,
                        events,
                        seats,
                        locations
                    RESTART IDENTITY CASCADE
                """)
            )


@pytest.fixture
async def event_service(test_container: AsyncContainer) -> AsyncGenerator[EventService, None]:
    async with test_container() as request_container:
        yield await request_container.get(EventService)


@pytest.fixture
async def postgres_event_queue(
    test_container: AsyncContainer,
) -> AsyncGenerator[PostgresEventQueue, None]:
    async with test_container() as request_container:
        queue = await request_container.get(PostgresEventQueue)
        yield queue


@pytest.fixture
async def running_test_app(test_app: FastAPI) -> FastAPI:
    async with LifespanManager(test_app):
        yield test_app
