import asyncio
import logging

from afisha.application.dto import (
    EventDashboard,
    OccupancyDashboard,
    OccupancyRead,
    SalesDashboard,
    SalesRead,
)
from afisha.exceptions import DashboardUnavailableError, ForbiddenError
from afisha.infrastracture.postgres.manager import DatabaseManager

logger = logging.getLogger(__name__)

class EventAnalyticsService:
    def __init__(self, db: DatabaseManager) -> None:
        self.db = db

    async def get_dashboard(
            self,
            event_id: int,
            organizer_id: int
    ) -> EventDashboard:
        event = await self.db.events.get_event(event_id)

        if event.organizer_id != organizer_id:
            raise ForbiddenError()

        try:
            async with asyncio.TaskGroup() as tg:
                task_sales = tg.create_task(self.db.bookings.get_sales(event_id, organizer_id))
                task_occupancy = tg.create_task(self.db.event_seats.get_occupancy(event_id))
        except* Exception:
            logger.exception("Failed to get analytics from DB")
            raise DashboardUnavailableError()

        sales = task_sales.result()
        occupancy = task_occupancy.result()

        sales = self._build_sales_dashboard(sales)
        occupancy = self._build_occupancy_dashboard(occupancy)

        return EventDashboard(
            event_title=event.title,
            starts_at=event.starts_at,
            sales=sales,
            occupancy=occupancy
        )

    def _build_sales_dashboard(self, sales: SalesRead) -> SalesDashboard:
        return SalesDashboard(
                paid_orders=sales.paid_orders,
                sold_tickets=sales.sold_tickets,
                revenue=sales.revenue,
                average_order=sales.average_order,
        )

    def _build_occupancy_dashboard(self, occupancy: OccupancyRead) -> OccupancyDashboard:
        return OccupancyDashboard(
                total=occupancy.total,
                available=occupancy.available,
                reserved=occupancy.reserved,
                sold=occupancy.sold,
                occupancy_percent=occupancy.occupancy_percent
        )
