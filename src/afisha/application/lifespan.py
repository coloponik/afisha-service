import logging
from contextlib import asynccontextmanager

from dishka import Scope, AsyncContainer
from fastapi import FastAPI

from afisha.infrastracture.postgres.add_event_data import add_event_data_to_db
from afisha.infrastracture.postgres.manager import PostgresClient

logger = logging.getLogger(__name__)


def create_lifespan(container: AsyncContainer):
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logger.info("Afisha lifespan started")

        await seed_database(container)
        try:
            yield
        finally:
            logger.info("Afisha shutdown started")

    return lifespan


async def seed_database(container: AsyncContainer):
    async with container(scope=Scope.REQUEST) as req_container:
        postgres = await req_container.get(PostgresClient)

        await add_event_data_to_db(postgres.session_maker)
