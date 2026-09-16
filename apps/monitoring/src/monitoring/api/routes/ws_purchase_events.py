from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, WebSocket

from monitoring.infrastructure.websocket.manager import WebsocketManager, send_messages_to_client

purchase_events_router = APIRouter(
    tags=["Вебсокет: События покупки билетов"]
)


@purchase_events_router.websocket("/ws/payments")
@inject
async def get_purchase_events(
    ws: WebSocket,
    ws_manager: FromDishka[WebsocketManager],
):
    async with ws_manager.connect(ws) as client:
        await send_messages_to_client(client)
