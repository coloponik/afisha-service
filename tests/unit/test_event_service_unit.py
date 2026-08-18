from fastapi import Request
from unittest.mock import MagicMock, AsyncMock

from afisha.services.event import EventService


class TestEventService:
    async def test_deduplicate_view_for_same_ip_and_event(
            self,
            event_service: EventService
    ) -> None:
        event_id = 1

        request = MagicMock(spec=Request)
        request.client.host = "127.0.0.1"

        event_service.cache.register_event_view = AsyncMock(
            side_effect=[True, False]
        )
        event_service.queue.add_event_view = AsyncMock()

        await event_service.register_user_view(event_id, request)
        await event_service.register_user_view(event_id, request)

        event_service.queue.add_event_view.assert_awaited_once_with(event_id)


