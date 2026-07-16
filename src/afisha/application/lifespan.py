import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from afisha.infrastracture.postgres.add_event_data import add_event_data_to_db


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Afisha's lifespan is started")
    # await add_event_data_to_db()
    yield
    logger.info("Afisha's shutdown started")
