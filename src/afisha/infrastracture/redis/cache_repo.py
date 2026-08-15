import json
import random

from redis.asyncio.lock import Lock

from afisha.application.dto import EventRead
from afisha.infrastracture.redis.manager import RedisManager


class CacheRepo:
    def __init__(self, redis: RedisManager) -> None:
        self._client = redis.client

    def lock(self, *args, **kwargs) -> Lock:
        return self._client.lock(*args, **kwargs)

    def _get_event_key(self, event_id: int) -> str:
        return f"event:{event_id}"

    def _get_ttl_with_jitter(self, ttl: int) -> int:
        jitter = int(ttl * 0.1)
        ttl_with_jitter = ttl + random.randint(-jitter, jitter)
        return ttl_with_jitter

    async def get_event(self, event_id: int) -> EventRead | None:
        res = await self._client.get(self._get_event_key(event_id))

        if res is None:
            return None

        return EventRead.model_validate(json.loads(res))

    async def set_event(self, event_id: int, event: EventRead, ttl: int = 30) -> None:
        await self._client.set(
            name=self._get_event_key(event_id),
            value=event.model_dump_json(),
            ex=self._get_ttl_with_jitter(ttl)
        )
