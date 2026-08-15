import logging

from redis.exceptions import LockError

from afisha.application.dto import EventData, EventRead
from afisha.exceptions import LockTimeoutError
from afisha.infrastracture.postgres.manager import DatabaseManager
from afisha.infrastracture.redis.cache_repo import CacheRepo


logger = logging.getLogger(__name__)


class EventService:
    def __init__(
            self,
            db: DatabaseManager,
            cache: CacheRepo
    ) -> None:
        self.db = db
        self.cache = cache

    async def get_event(self, event_id: int) -> EventData:
        event = await self.cache.get_event(event_id=event_id)

        if event is not None:
            return EventData.model_validate(event)

        event = await self._refresh_event_with_lock(event_id)

        return EventData.model_validate(event)

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

                event = await self.db.events.get_event(event_id=event_id)
                await self.cache.set_event(event_id=event.id, event=event)

            return event
        except LockError as exc:
            logger.warning("Failed to acquire event lock", extra={"event_id": event_id})
            raise LockTimeoutError() from exc
