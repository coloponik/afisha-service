import asyncio
import datetime
import logging

from afisha.application.dto import CheckoutResponse, CheckoutBooking, BookingRead, ProtectionQuote, \
    PaymentQuote, BookingCreate
from afisha.exceptions import SeatAlreadyReservedError, SeatsNotFoundError, PaymentUnavailableError
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
            payload: BookingCreate,
            user_id: int
    ) -> CheckoutResponse:
        booking = await self.prepare_booking(event_id, payload.seat_ids, user_id)

        task_payment = asyncio.create_task(self.payment_connector.get_commission(
            booking_id=booking.id,
            amount=booking.amount,
            currency="USD"
        ))

        event = await self.db.events.get_event(event_id)

        task_protection = asyncio.create_task(self.protection_connector.get_protection_info(
            booking_id=booking.id,
            ticket_amount=booking.amount,
            event_category=event.category,
            event_starts_at=event.starts_at
        ))

        payment, protection = await asyncio.gather(
            task_payment,
            task_protection,
            return_exceptions=True
        )

        payment = self._validate_payment_response(payment)
        protection = self._handle_protection_response(protection)

        protection_price = protection.price if protection else None
        with_protection = protection.available if protection else False

        await self.db.bookings.update_checkout_details(
            booking_id=booking.id,
            payment_commission=payment.commission,
            protection_price=protection_price,
            with_protection=with_protection
        )
        await self.db.commit()

        booking.payment_commission = payment.commission
        booking.protection_price = protection_price
        booking.with_protection = with_protection

        seats = await self.db.seats.get_seats(payload.seat_ids)

        booking = self._build_checkout_booking(booking, event, seats)
        protection = self._build_checkout_protection(protection)

        return CheckoutResponse(
            booking=booking,
            payment=PaymentQuote(
                commission=payment.commission,
                total=payment.total,
                payment_methods=payment.payment_methods,
                expires_at=payment.expires_at
            ),
            protection=protection
        )

    async def prepare_booking(
            self,
            event_id: int,
            seat_ids: list[int],
            user_id: int
    ) -> BookingRead:
        async with self.db.transaction() as db:
            event_seats = await db.event_seats.get_event_seats(
                event_id=event_id,
                seat_ids=seat_ids
            )

            self.validate_event_seats(event_seats, seat_ids)

            amount = sum(seat.price for seat in event_seats)
            reserved_until = datetime.datetime.now(datetime.UTC) + datetime.timedelta(
                minutes=15)

            await db.event_seats.reserve_seats(
                event_seats=event_seats,
                reserved_until=reserved_until
            )

            booking = await db.bookings.create_booking(
                event_id=event_id,
                user_id=user_id,
                amount=amount,
                payment_commission=None,
                protection_price=None,
                with_protection=False,
                status=BookingStatus.pending_payment,
                reserved_until=reserved_until
            )

        return booking

    def validate_event_seats(
            self,
            event_seats: list[EventSeat],
            seat_ids: list[int]
    ) -> None:
        if len(event_seats) != len(seat_ids):
            raise SeatsNotFoundError()

        for seat in event_seats:
            current_time = datetime.datetime.now(datetime.UTC)
            if (
                    seat.status != SeatStatus.available and
                    seat.reserved_until > current_time
            ):
                raise SeatAlreadyReservedError()

    def _build_checkout_booking(
            self,
            booking: BookingRead,
            event,
            seats
    ) -> CheckoutBooking:
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

    def _build_checkout_protection(self, protection) -> ProtectionQuote | None:
        if protection:
            return ProtectionQuote(
                available=protection.available,
                price=protection.price,
                covered_amount=protection.covered_amount,
                description=protection.description
            )
        return None

    def _validate_payment_response(
            self,
            payment: PaymentQuote | Exception
    ) -> PaymentQuote:
        if isinstance(payment, Exception):
            logger.error(
                f"FAILED to receive response from Payment API:",
                exc_info=payment
            )
            raise PaymentUnavailableError() from payment

        return payment

    def _handle_protection_response(
            self,
            protection: ProtectionQuote | Exception
    ) -> ProtectionQuote | None:
        if isinstance(protection, Exception):
            logger.error(
                f"Protection service UNAVAILABLE, continue without protection",
                exc_info=protection
            )
            protection = None
        return protection
