import asyncio
import datetime
import logging

from sqlalchemy.exc import OperationalError

from afisha.application.dto import CheckoutResponse, CheckoutBooking
from afisha.exceptions import SeatAlreadyReservedError, SeatsNotFoundError
from afisha.infrastracture.postgres.models import BookingStatus, EventSeat, SeatStatus, Booking


logger = logging.getLogger(__name__)


class BookingService:
    def __init__(self, db, payment_connector, protection_connector) -> None:
        self.db = db
        self.payment_connector = payment_connector
        self.protection_connector = protection_connector

    async def reserve(
            self,
            event_id: int,
            payload: list[int],
            user_id: int
    ) -> CheckoutResponse:

        amount, reserved_until = await self.prepare_reservation(event_id, payload)

        # TODO: конкурентно запросить Payment API и Protection API для расчета checkout.
        with_protection = False
        protection = None

        task_payment = await asyncio.create_task(
            self.payment_connector.get_commision()
        )
        task_protection = await asyncio.create_task(
            self.protection_connector.get_protection_price()
        )

        payment = task_payment.result()
        protection = task_protection.result() or None

        booking = await self.db.booking.add_booking(
            event_id=event_id,
            user_id=user_id,
            amount=amount,
            payment_commission=payment.commission,
            protection_price=protection.price,
            with_protection=with_protection,
            status=BookingStatus.pending_payment,
            reserved_until=reserved_until
        )

        event = await self.db.event.get_event(event_id)
        seats = await self.db.seats.get_seats(payload)
        booking = self._build_checkout_booking(booking, event, seats)

        return CheckoutResponse(
            booking=booking,
            payment=payment,
            protection=protection
        )

    async def prepare_reservation(
            self,
            event_id: int,
            seat_ids: list[int]
    ) -> tuple[int, datetime]:
        async with self.db.transaction() as db:
            event_seats = await db.events_seats.get_event_seats(
                event_id=event_id,
                seat_ids=seat_ids
            )

            self.validate_event_seats(event_seats, seat_ids)

            amount = sum(seat.price for seat in event_seats)
            reserved_until = datetime.datetime.now(datetime.UTC) + datetime.timedelta(
                minutes=15)

            await db.events_seats.reserve_seats(
                event_seats=event_seats,
                reserved_until=reserved_until
            )

        return amount, reserved_until

    def validate_event_seats(self, event_seats: list[EventSeat], seat_ids: list[int]) -> None:
        if len(event_seats) != len(seat_ids):
            raise SeatsNotFoundError()
            pass

        for seat in event_seats:
            if seat.status != SeatStatus.available:
                raise SeatAlreadyReservedError()
                pass

    async def _build_checkout_booking(self, booking: Booking, event, seats) -> CheckoutBooking:
        return CheckoutBooking(
            id=booking.id,
            event_title=event.title,
            starts_at=event.starts_at,
            seats=[seat.model_dump() for seat in seats],
            base_amount=booking.amount,
            payment_commission=booking.payment_commission,
            protection_price=booking.protection_price,
            with_protection=booking.with_protection,
            reserved_until=booking.reserved_until
        )
