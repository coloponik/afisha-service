import httpx
import pytest

from asgi_lifespan import LifespanManager
from dishka import make_async_container, AsyncContainer, Scope
from sqlalchemy import text

from afisha.application.app import create_fastapi_app
from afisha.application.providers import ConfigProvider, ServiceProvider
from afisha.core.config import Settings
from afisha.infrastracture.postgres.manager import PostgresClient
from afisha.infrastracture.providers import PostgresProvider
from tests.mock_providers import MockConnectorsProvider


@pytest.fixture(scope="session")
def test_settings():
    return Settings()


def make_test_container(settings: Settings) -> AsyncContainer:
    return make_async_container(
        ConfigProvider(settings),
        ServiceProvider(),
        PostgresProvider(),
        MockConnectorsProvider()
    )


@pytest.fixture
async def test_container(test_settings):
    container = make_test_container(test_settings)
    yield container
    await container.close()


@pytest.fixture
async def test_app(test_settings, test_container):
    app = create_fastapi_app(test_settings, test_container)
    return app


@pytest.fixture
async def async_client(test_app):
    async with LifespanManager(test_app):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=test_app),
            base_url="http://test"
        ) as client:
            yield client


@pytest.fixture(autouse=True)
async def clean_database(test_container):
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
