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

    async def get_event_view(self, event_id: int) -> EventView | None:
        query = (
            select(EventView)
            .where(EventView.event_id == event_id)
        )

        return await self.session.scalar(query)

    async def update_or_create_event_view(self, event_views: list[dict]) -> None:
        stmt = insert(EventView).values(event_views)
        stmt = stmt.on_conflict_do_update(
                index_elements=[EventView.event_id],
                set_={
                    "views_count": EventView.views_count + stmt.excluded.views_count
                }
        )

        await self.session.execute(stmt)

