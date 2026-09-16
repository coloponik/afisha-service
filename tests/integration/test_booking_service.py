from unittest.mock import AsyncMock

from fastapi import FastAPI
from sqlalchemy import select

from afisha.application.dto import ProtectionRetryData
from afisha.infrastructure.api_connectors.schemas import CalculatedProtectionData
from afisha.infrastructure.postgres.manager import DatabaseManager
from afisha.infrastructure.postgres.models import Booking, EventSeat, SeatStatus
from afisha.services.booking import BookingService


class TestBookingService:
    async def test_release_expired_bookings_success(
            self,
            running_test_app: FastAPI,
            db: DatabaseManager,
            booking_service: BookingService,
            fake_bookings
    ):
        fake_event_id = 1
        async with db.transaction() as db:
            event_seat = await db.event_seats.session.scalar(
                select(EventSeat)
            )

            created_bookings = []

            for booking_data in fake_bookings:
                booking = await db.bookings.create_booking(
                    event_id=fake_event_id,
                    **booking_data,
                )
                created_bookings.append(booking)

            expired, active, paid = created_bookings

            await db.event_seats.reserve_seats(
                [event_seat],
                reserved_until=expired.reserved_until,
                booking_id=expired.id,
            )

            event_seat_id = event_seat.id

        await booking_service.release_expired_bookings()

        async with db.transaction() as db:
            existing_booking_ids = set(
                await db.bookings.session.scalars(
                    select(Booking.id)
                    .where(Booking.id.in_([expired.id, active.id, paid.id]))
                )
            )

            event_seat = await db.event_seats.session.scalar(
                select(EventSeat)
                .where(EventSeat.id == event_seat_id)
            )

        assert expired.id not in existing_booking_ids
        assert active.id in existing_booking_ids
        assert paid.id in existing_booking_ids

        assert event_seat.status == SeatStatus.available
        assert event_seat.booking_id is None
        assert event_seat.reserved_until is None

    async def test_protection_not_updated_for_paid_booking(
            self,
            running_test_app: FastAPI,
            db: DatabaseManager,
            booking_service: BookingService,
            fake_bookings: list
    ) -> None:
        booking = await db.bookings.create_booking(
            event_id=1,
            **fake_bookings[2]
        )
        await db.commit()

        booking_service.protection_connector.get_protection_info = AsyncMock(
            return_value=CalculatedProtectionData(
                available=True,
                price=500,
                covered_amount=1000,
                description="test",
            )
        )

        event = await db.events.get_event(booking.event_id)

        retry_data = ProtectionRetryData(
            booking_id=booking.id,
            ticket_amount=booking.amount,
            event_category=event.category,
            event_starts_at=event.starts_at,
        )

        await booking_service.fetch_and_save_protection(retry_data)

        updated_booking = await db.bookings.session.scalar(
            select(Booking)
            .where(Booking.id == booking.id)
        )

        assert updated_booking.protection_price is None
        assert updated_booking.with_protection is False
