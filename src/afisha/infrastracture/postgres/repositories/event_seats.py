from datetime import datetime

from sqlalchemy import Float, Numeric, and_, cast, func, or_, select, update

from afisha.application.dto import OccupancyRead
from afisha.infrastracture.postgres.models import (
    Booking,
    BookingStatus,
    EventSeat,
    SeatStatus,
)
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

        result = await self.session.scalars(query)
        seats = result.all()

        return list(seats)

    async def reserve_seats(
            self,
            event_seats: list[EventSeat],
            reserved_until: datetime,
            booking_id: int
    ) -> None:
        for seat in event_seats:
            seat.status = SeatStatus.reserved
            seat.reserved_until = reserved_until
            seat.booking_id = booking_id

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

    async def get_occupancy(self, event_id: int) -> OccupancyRead:
        query = (
            select(
                func.count(EventSeat.id)
                .label("total_seats"),

                func.count(EventSeat.id)
                .filter(
                    or_(
                        EventSeat.status == SeatStatus.available,
                        and_(
                            EventSeat.status == SeatStatus.reserved,
                            EventSeat.reserved_until <= func.now()
                        )
                    )
                )
                .label("available_seats"),

                func.count(EventSeat.id)
                .filter(
                    and_(
                        EventSeat.status == SeatStatus.reserved,
                        EventSeat.reserved_until > func.now(),
                        Booking.status == BookingStatus.pending_payment
                    )
                )
                .label("reserved_seats"),

                func.count(EventSeat.id)
                .filter(
                    EventSeat.status == SeatStatus.sold
                )
                .label("sold_seats"),

                func.round(
                    (
                        cast(
                            func.count(EventSeat.id)
                            .filter(
                                or_(
                                    EventSeat.status == SeatStatus.sold,
                                    and_(
                                        EventSeat.status == SeatStatus.reserved,
                                        EventSeat.reserved_until > func.now(),
                                        Booking.status == BookingStatus.pending_payment
                                    )
                                )
                            ),
                            Numeric
                        )
                        /
                        func.nullif(func.count(EventSeat.id), 0)
                        * 100
                    ),
                    2
                )
                .cast(Float)
                .label("occupancy_percent")
            )
            .select_from(EventSeat)
            .outerjoin(
                Booking,
                Booking.id == EventSeat.booking_id
            )
            .where(EventSeat.event_id == event_id)
        )

        result = await self.session.execute(query)
        analytics = result.one()

        return OccupancyRead(
            total=analytics.total_seats,
            available=analytics.available_seats,
            reserved=analytics.reserved_seats,
            sold=analytics.sold_seats,
            occupancy_percent=analytics.occupancy_percent
        )
