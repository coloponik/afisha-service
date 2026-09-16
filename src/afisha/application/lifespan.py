import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from dishka import AsyncContainer, Scope
from fastapi import FastAPI
from faststream.kafka import KafkaBroker
from starlette.types import Lifespan

from afisha.infrastructure.postgres.add_event_data import add_event_data_to_db
from afisha.infrastructure.postgres.manager import PostgresClient
from afisha.infrastructure.postgres.queue import PostgresEventQueue
from afisha.services.purchase_simulator import PurchaseSimulationService

logger = logging.getLogger(__name__)


def create_lifespan(container: AsyncContainer) -> Lifespan:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator:
        logger.info("Afisha lifespan started")

        await seed_database(container)

        postgres_event_queue = await container.get(PostgresEventQueue)
        kafka_broker = await container.get(KafkaBroker)
        purchase_simulation = await container.get(PurchaseSimulationService)

        postgres_event_queue.start()
        await kafka_broker.start()

        simulation_task = asyncio.create_task(purchase_simulation.run_simulation())

        try:
            yield
        finally:
            logger.info("Afisha shutdown started")

            simulation_task.cancel()

            await asyncio.gather(
                simulation_task,
                return_exceptions=True
            )

            await postgres_event_queue.stop()
            await kafka_broker.stop()

    return lifespan


async def seed_database(container: AsyncContainer) -> None:
    async with container(scope=Scope.REQUEST) as req_container:
        postgres = await req_container.get(PostgresClient)

        await add_event_data_to_db(postgres.session_maker)
