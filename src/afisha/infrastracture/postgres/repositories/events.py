from sqlalchemy import select

from afisha.application.dto import EventRead
from afisha.infrastracture.postgres.models import Event
from afisha.infrastracture.postgres.repositories.base import BaseRepo


class EventRepo(BaseRepo):
    async def get_event(self, event_id: int) -> EventRead:
        query = (
            select(Event)
            .where(Event.id == event_id)
        )

        event = await self.session.scalar(query)

        if event is None:
            # raise EventNotFoundError()
            pass

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
