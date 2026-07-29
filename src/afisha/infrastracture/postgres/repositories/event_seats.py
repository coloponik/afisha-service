from sqlalchemy import select, and_, insert, update

from afisha.application.dto import EventSeatRead
from afisha.infrastracture.postgres.models import EventSeat, SeatStatus
from afisha.infrastracture.postgres.repositories.base import BaseRepo


class EventSeatRepo(BaseRepo):
    async def get_event_seats(self, event_id: int, seat_ids: list[int]) -> list[EventSeat]:
        query = (
            select(EventSeat)
            .where(
                and_(
                    EventSeat.event_id == event_id,
                    EventSeat.seat_id.in_(seat_ids)
                )
            )
            .with_for_update(nowait=True)
        )

        resp = await self.session.scalars(query)
        seats = resp.all()

        return list(seats)

    async def reserve_seats(self, event_seats: list[EventSeat], reserved_until) -> None:
        for seat in event_seats:
            seat.status = SeatStatus.reserved
            seat.reserved_until = reserved_until

    async def release_seats(self, booking_id: int) -> None:
        stmt = (
            update(EventSeat)
            .where(EventSeat.booking_id == booking_id)
            .values(
                status=SeatStatus.available,
                reserved_until=None,
                booking_id=None
            )
        )

        await self.session.execute(stmt)
