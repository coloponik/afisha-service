import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from dishka import AsyncContainer, Scope
from fastapi import FastAPI
from starlette.types import Lifespan

from afisha.infrastracture.postgres.add_event_data import add_event_data_to_db
from afisha.infrastracture.postgres.manager import PostgresClient
from afisha.infrastracture.postgres.queue import PostgresEventQueue

logger = logging.getLogger(__name__)


def create_lifespan(container: AsyncContainer) -> Lifespan:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator:
        logger.info("Afisha lifespan started")

        await seed_database(container)

        postgres_event_queue = await container.get(PostgresEventQueue)
        postgres_event_queue.start()

        try:
            yield
        finally:
            logger.info("Afisha shutdown started")
            await postgres_event_queue.stop()

    return lifespan


async def seed_database(container: AsyncContainer) -> None:
    async with container(scope=Scope.REQUEST) as req_container:
        postgres = await req_container.get(PostgresClient)

        await add_event_data_to_db(postgres.session_maker)
