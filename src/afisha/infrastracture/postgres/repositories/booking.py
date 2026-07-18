from datetime import datetime

from sqlalchemy import insert

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
    ) -> int:
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
            .returning(Booking.id)
        )

        booking_id = await self.session.scalar(stmt)

        return booking_id
