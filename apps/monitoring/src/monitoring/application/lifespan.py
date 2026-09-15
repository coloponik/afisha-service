import logging
from contextlib import asynccontextmanager

from dishka import AsyncContainer
from fastapi import FastAPI


logger = logging.getLogger(__name__)


def create_lifespan(container: AsyncContainer):
    @asynccontextmanager
    async def lifespan(_: FastAPI):
        logger.info("Monitoring service lifespan started")
        try:
            yield
        finally:
            logger.info("Monitoring service shutdown started")
            pass

    return lifespan
