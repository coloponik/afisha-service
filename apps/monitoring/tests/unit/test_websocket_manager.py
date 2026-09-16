import asyncio
from unittest.mock import AsyncMock

from monitoring.infrastructure.websocket.manager import WebsocketManager, send_messages_to_client


class TestWebsocketManager:
    async def test_broadcast_sends_message_to_all_clients(
            self,
            websocket_manager: WebsocketManager,
            websocket_client_factory,
    ):
        client_1 = websocket_client_factory()
        client_2 = websocket_client_factory()

        websocket_manager._clients = {
            "client-1": client_1,
            "client-2": client_2,
        }

        message = [{"event_id": 1, "payments_count": 3}]

        await websocket_manager.broadcast(message)

        assert await client_1.queue.get() == message
        assert await client_2.queue.get() == message

    async def test_slow_client_does_not_block_other_client(
            self,
            websocket_manager: WebsocketManager,
            websocket_client_factory
    ) -> None:

        slow_started = asyncio.Event()
        fast_sent = asyncio.Event()

        async def slow_send(*args, **kwargs) -> None:
            slow_started.set()
            await asyncio.sleep(10)

        async def fast_send(*args, **kwargs) -> None:
            fast_sent.set()

        slow_client = websocket_client_factory()
        fast_client = websocket_client_factory()

        slow_client.ws.send_json.side_effect = slow_send
        fast_client.ws.send_json.side_effect = fast_send

        websocket_manager._clients = {
            "slow": slow_client,
            "fast": fast_client,
        }

        slow_sender = asyncio.create_task(
            send_messages_to_client(slow_client)
        )
        fast_sender = asyncio.create_task(
            send_messages_to_client(fast_client)
        )

        message = [{"event_id": 1}]

        try:
            await websocket_manager.broadcast(message)

            await asyncio.wait_for(
                slow_started.wait(),
                timeout=0.5,
            )

            await asyncio.wait_for(
                fast_sent.wait(),
                timeout=0.5,
            )

            fast_client.ws.send_json.assert_awaited_once_with(message)

            assert not slow_sender.done()

        finally:
            slow_sender.cancel()
            fast_sender.cancel()

            await asyncio.gather(
                slow_sender,
                fast_sender,
                return_exceptions=True,
            )
