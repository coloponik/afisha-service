import asyncio
import logging
from contextlib import asynccontextmanager

from dishka import AsyncContainer
from fastapi import FastAPI
from faststream.kafka import KafkaBroker

from monitoring.services.websocket_purchase_broadcaster import WebSocketPurchaseBroadcaster

logger = logging.getLogger(__name__)


def create_lifespan(container: AsyncContainer):
    @asynccontextmanager
    async def lifespan(_: FastAPI):
        logger.info("Monitoring service lifespan started")

        broker = await container.get(KafkaBroker)
        ws_broadcaster = await container.get(WebSocketPurchaseBroadcaster)

        await broker.start()

        ws_broadcaster_task = asyncio.create_task(
            ws_broadcaster.run()
        )

        try:
            yield
        finally:
            logger.info("Monitoring service shutdown started")
            ws_broadcaster_task.cancel()

            try:
                await ws_broadcaster_task
            except asyncio.CancelledError:
                pass

            await broker.stop()
            await container.close()

    return lifespan
