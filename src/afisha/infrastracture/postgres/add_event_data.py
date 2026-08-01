from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker

# from afisha.infrastracture.postgres.db import engine
from afisha.infrastracture.postgres.models import Event, EventSeat, Location, Seat, BookingStatus, \
    Booking, SeatStatus


async def add_event_data_to_db(session_maker: async_sessionmaker) -> None:
    async with session_maker() as db:
        async with db.begin():
            if await db.scalar(select(func.count(Location.id))):
                print("Тестовые данные уже существуют")
                return

            location = Location(
                name="Центральный зал",
                city="Москва",
                address="Тверская улица, 1",
            )
            db.add(location)
            await db.flush()

            seats = []
            for row in range(1, 6):
                for number in range(1, 11):
                    seats.append(
                        Seat(
                            location_id=location.id,
                            sector="Основной сектор",
                            row=row,
                            number=number,
                            x=number * 50,
                            y=row * 50,
                        )
                    )
            db.add_all(seats)
            await db.flush()

            event = Event(
                organizer_id=1,
                location_id=location.id,
                title="Python Конференция",
                description="Тестовое мероприятие для домашнего задания",
                category="конференция",
                starts_at=datetime.now(timezone.utc) + timedelta(days=30),
                base_price=5000,
            )
            db.add(event)
            await db.flush()

            db.add_all(
                EventSeat(event_id=event.id, seat_id=seat.id, price=event.base_price)
                for seat in seats
            )

            booking = Booking(
                event_id=event.id,
                user_id=1,
                amount=1000,
                payment_commission=100,
                protection_price=None,
                with_protection=False,
                status=BookingStatus.paid,
                reserved_until=datetime.now(timezone.utc)
            )
            db.add(booking)
            await db.flush()

            event_seat = await db.scalar(
                select(EventSeat)
                .where(
                    EventSeat.event_id == event.id,
                    EventSeat.seat_id == seats[0].id,
                )
            )

            event_seat.status = SeatStatus.sold
            event_seat.booking_id = booking.id
            event_seat.reserved_until = None

        print("Тестовые данные созданы")


# if __name__ == "__main__":
#     import asyncio
#
#     asyncio.run(add_event_data_to_db())
