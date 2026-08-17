import asyncio
import logging

from afisha.exceptions import EventViewPersistenceError
from afisha.infrastracture.postgres.manager import PostgresClient

logger = logging.getLogger(__name__)


class PostgresEventQueue:
    def __init__(self, postgres: PostgresClient) -> None:
        self._queue = asyncio.Queue()
        self._postgres = postgres
        self._worker_task: asyncio.Task | None = None
        self._stopping = False

    async def add_event_view(self, event_id: int) -> None:
        print("ADD NEW EVENT")
        await self._queue.put(event_id)

    def start(self) -> None:
        self._worker_task = asyncio.create_task(self._flush_events())

    async def stop(self) -> None:
        self._stopping = True

        await self._queue.put(None)

        if self._worker_task is not None:
            await self._worker_task

    async def _flush_events(self) -> None:
        events = []

        while True:
            try:
                event = await asyncio.wait_for(self._queue.get(), timeout=5)

                if event is None:
                    logger.info("Shutdown signal received")
                    print("Shutdown signal received")
                    break

                events.append(event)

                if len(events) >= 10:
                    await self._insert_events_to_db(events)

            except asyncio.TimeoutError:
                if events:
                    await self._insert_events_to_db(events)

        if events:
            logger.info("Flushing %d remaining events", len(events))
            print(f"Flushing {len(events)} remaining events")
            await self._insert_events_to_db(events)

    async def _insert_events_to_db(self, events: list) -> None:
        try:
            async with self._postgres.session() as db:
                async with db.transaction() as tr:
                    await tr.events.update_or_create_event_view(events)

            print("INSERTED EVENT TO DB")
            events.clear()
        except Exception as exc:
            logger.exception("Failed to persist event views")
            if self._stopping:
                raise EventViewPersistenceError(
                    "Failed to persist event views during shutdown"
                ) from exc



