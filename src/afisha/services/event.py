import asyncio
import logging
from ipaddress import ip_address
from fastapi import Request

from redis.exceptions import LockError

from afisha.application.dto import EventData, EventRead
from afisha.exceptions import LockTimeoutError
from afisha.infrastracture.postgres.manager import DatabaseManager
from afisha.infrastracture.postgres.queue import PostgresEventQueue
from afisha.infrastracture.redis.cache_repo import CacheRepo


logger = logging.getLogger(__name__)


class EventService:
    def __init__(
            self,
            db: DatabaseManager,
            cache: CacheRepo,
            queue: PostgresEventQueue
    ) -> None:
        self.db = db
        self.cache = cache
        self.queue = queue

    async def get_event(self, event_id: int, request: Request) -> EventData:
        event = await self.cache.get_event(event_id=event_id)

        if event is None:
            event = await self._refresh_event_with_lock(event_id)

        asyncio.create_task(self.register_user_view(event_id, request))

        return EventData.model_validate(event)

    async def register_user_view(self, event_id: int, request: Request) -> None:
        try:
            normalized_ip = str(ip_address(request.client.host))
            is_new = await self.cache.register_event_view(event_id=event_id, ip=normalized_ip)

            if is_new:
                await self.queue.add_event_view(event_id)
        except Exception:
            logger.exception(
                "Failed to register user event view",
                extra={"event_id": event_id}
            )

    async def _refresh_event_with_lock(self, event_id: int) -> EventRead:
        try:
            async with self.cache.lock(
                name=f"locks:afisha-api-event:{event_id}",
                timeout=5,
                blocking_timeout=3
            ):
                event = await self.cache.get_event(event_id=event_id)
                if event is not None:
                    return event

                async with self.db.transaction() as db:
                    event = await db.events.get_event(event_id=event_id)

                await self.cache.set_event(event_id=event.id, event=event)

            return event
        except LockError as exc:
            logger.warning("Failed to acquire event lock", extra={"event_id": event_id})
            raise LockTimeoutError() from exc
