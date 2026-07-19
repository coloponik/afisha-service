from sqlalchemy import select

from afisha.application.dto import SeatRead
from afisha.infrastracture.postgres.models import Seat
from afisha.infrastracture.postgres.repositories.base import BaseRepo


class SeatRepo(BaseRepo):
    async def get_seats(self, seat_ids: list[int]) -> list[SeatRead]:
        query = (
            select(Seat)
            .where(Seat.id.in_(seat_ids))
        )

        res = await self.session.scalars(query)
        seats = res.all()

        return [
            SeatRead(
                id=seat.id,
                location_id=seat.location_id,
                sector=seat.sector,
                row=seat.row,
                number=seat.number,
                x=seat.x,
                y=seat.y
            )
            for seat in seats
        ]
