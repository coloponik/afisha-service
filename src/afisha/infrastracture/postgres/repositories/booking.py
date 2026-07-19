from datetime import datetime

from sqlalchemy import insert

from afisha.application.dto import CheckoutBooking
from afisha.infrastracture.postgres.models import Booking
from afisha.infrastracture.postgres.repositories.base import BaseRepo


class BookingRepo(BaseRepo):
    async def add_booking(
            self,
            event_id: int,
            user_id: int,
            amount: int,
            payment_commission: int,
            protection_price: int,
            with_protection: bool,
            status: str,
            reserved_until: datetime
    ) -> Booking:
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

        return booking

