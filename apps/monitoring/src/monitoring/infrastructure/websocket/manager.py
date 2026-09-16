import asyncio
import logging
from contextlib import asynccontextmanager
from dataclasses import dataclass
from uuid import uuid4

from fastapi import WebSocket, WebSocketDisconnect


logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class WebsocketClient:
    ws: WebSocket
    queue: asyncio.Queue


class WebsocketManager:
    def __init__(self):
        self._clients: dict[str, WebsocketClient] = {}

    @asynccontextmanager
    async def connect(self, ws: WebSocket):
        await ws.accept()

        client_id = uuid4().hex
        client = WebsocketClient(
            ws=ws,
            queue=asyncio.Queue(),
        )
        self._clients[client_id] = client

        try:
            yield client
        finally:
            self._clients.pop(client_id)

    async def broadcast(self, message):
        for client in self._clients.values():
            await client.queue.put(message)


async def send_messages_to_client(client: WebsocketClient):
    while True:
        message = await client.queue.get()

        try:
            await asyncio.wait_for(
                client.ws.send_json(message),
                timeout=2,
            )
        except WebSocketDisconnect:
            break
        except Exception:
            logger.exception("Failed to send WebSocket message to client")
