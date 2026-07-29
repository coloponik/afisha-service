from datetime import datetime

from sqlalchemy import insert, update

from afisha.application.dto import BookingRead
from afisha.infrastracture.postgres.models import Booking, BookingStatus
from afisha.infrastracture.postgres.repositories.base import BaseRepo


class BookingRepo(BaseRepo):
    async def create_booking(
            self,
            event_id: int,
            user_id: int,
            amount: int,
            payment_commission: int | None,
            protection_price: int | None,
            with_protection: bool,
            status: str,
            reserved_until: datetime
    ) -> BookingRead:
        stmt = (
            insert(Booking)
            .values(
                event_id=event_id,
                user_id=user_id,
                amount=amount,
                payment_commission=payment_commission,
                protection_price=protection_price,
                with_protection=with_protection,
                status=status,
                reserved_until=reserved_until
            )
            .returning(Booking)
        )

        res = await self.session.execute(stmt)
        booking = res.scalar_one()

        return BookingRead(
            id=booking.id,
            event_id=booking.event_id,
            user_id=booking.user_id,
            amount=booking.amount,
            payment_commission=booking.payment_commission,
            protection_price=booking.protection_price,
            with_protection=booking.with_protection,
            status=booking.status,
            reserved_until=booking.reserved_until
        )

    async def update_checkout_details(
            self,
            booking_id: int,
            payment_commission: int | None,
            protection_price: int | None,
            with_protection: bool,
    ) -> None:
        stmt = (
            update(Booking)
            .where(Booking.id == booking_id)
            .values(
                payment_commission=payment_commission,
                protection_price=protection_price,
                with_protection=with_protection
            )
        )

        await self.session.execute(stmt)

    async def cancel(self, booking_id: int) -> None:
        stmt = (
            update(Booking)
            .where(Booking.id == booking_id)
            .values(
                status=BookingStatus.cancelled
            )
        )

        await self.session.execute(stmt)
