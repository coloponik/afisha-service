import asyncio
from unittest.mock import AsyncMock, MagicMock

from fastapi import Request, FastAPI

from afisha.services.event import EventService


class TestEventService:
    async def test_concurrent_requests_fetch_event_once(
            self,
            running_test_app: FastAPI,
            event_service: EventService
    ) -> None:
        event_id = 1
        request = MagicMock(spec=Request)
        request.client.host = "127.0.0.1"

        await event_service.cache.delete(f"event:{event_id}")

        event_service.register_user_view = AsyncMock()

        tasks = [
            asyncio.create_task(event_service.get_event(event_id, request))
            for _ in range(3)
        ]

        results = await asyncio.gather(*tasks)

        assert all(result.id == event_id for result in results)

        assert results[0] == results[1] == results[2]

        cached_event = await event_service.cache.get_event(event_id)

        assert cached_event is not None
        assert cached_event.id == event_id
