from datetime import datetime

from sqlalchemy import insert, update, select, func, cast, Numeric, Integer, and_

from afisha.application.dto import BookingRead, SalesRead
from afisha.infrastracture.postgres.models import Booking, BookingStatus, EventSeat
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

    async def get_sales(self, event_id: int, organizer_id: int) -> SalesRead:
        sold_tickets = (
            select(func.count(EventSeat.id))
            .select_from(EventSeat)
            .join(Booking,
                  Booking.id == EventSeat.booking_id)
            .where(
                and_(
                    EventSeat.event_id == event_id,
                    Booking.status == BookingStatus.paid
                )
            )
            .label("sold_tickets")
        )

        query = (
            select(
                func.count(Booking.id)
                .label("paid_orders"),

                sold_tickets,

                func.coalesce(
                    func.sum(Booking.amount)
                    , 0
                )
                .label("revenue"),

                func.coalesce(
                    func.round(
                        func.avg(Booking.amount)
                    )
                    , 0
                )
                .cast(Integer)
                .label("average_order")
            )
            .select_from(Booking)
            .where(
                and_(
                    Booking.event_id == event_id,
                    Booking.status == BookingStatus.paid
                )
            )
        )

        result = await self.session.execute(query)
        analytics = result.one()

        return SalesRead(
            paid_orders=analytics.paid_orders,
            sold_tickets=analytics.sold_tickets,
            revenue=analytics.revenue,
            average_order=analytics.average_order
        )
