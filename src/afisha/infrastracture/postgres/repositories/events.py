from collections import Counter

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from afisha.application.dto import EventRead
from afisha.exceptions import EventNotFoundError
from afisha.infrastracture.postgres.models import Event, EventView
from afisha.infrastracture.postgres.repositories.base import BaseRepo


class EventRepo(BaseRepo):
    async def get_event(self, event_id: int) -> EventRead:
        query = (
            select(Event)
            .where(Event.id == event_id)
        )

        event = await self.session.scalar(query)

        if event is None:
            raise EventNotFoundError()

        return EventRead(
            id=event.id,
            organizer_id=event.organizer_id,
            location_id=event.location_id,
            title=event.title,
            description=event.description,
            category=event.category,
            starts_at=event.starts_at,
            base_price=event.base_price
        )

    async def update_or_create_event_view(self, events: list[int]) -> None:
        counts = Counter(events)

        if not counts:
            return

        values = [
            {
                "event_id": event_id,
                "views_count": count
            }
            for event_id, count in counts.items()
        ]

        stmt = insert(EventView).values(values)
        stmt = stmt.on_conflict_do_update(
                index_elements=[EventView.event_id],
                set_={
                    "views_count": EventView.views_count + stmt.excluded.views_count
                }
        )

        await self.session.execute(stmt)

