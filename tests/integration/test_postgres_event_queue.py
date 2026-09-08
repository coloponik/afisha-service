from fastapi import FastAPI

from afisha.infrastracture.postgres.manager import DatabaseManager
from afisha.infrastracture.postgres.queue import PostgresEventQueue


class TestPostgresEventQueue:
    async def test_graceful_shutdown_flushes_and_consolidates_event_views(
            self,
            running_test_app: FastAPI,
            db: DatabaseManager,
            postgres_event_queue: PostgresEventQueue
    ) -> None:
        event_id = 1
        views_to_add = 7

        event_view = await db.events.get_event_view(event_id=event_id)
        initial_views = 0
        if event_view is not None:
            initial_views = event_view.views_count

        for _ in range(views_to_add):
            await postgres_event_queue.add_event_view(event_id)

        await postgres_event_queue.stop()

        event_view = await db.events.get_event_view(event_id=event_id)

        assert event_view.views_count == initial_views + views_to_add

