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
from afisha.infrastructure.postgres.manager import DatabaseManager
from afisha.infrastructure.tasks.publisher import TaskPublisher

logger = logging.getLogger(__name__)

class EventAnalyticsService:
    def __init__(
            self,
            db: DatabaseManager,
            task_publisher: TaskPublisher
    ) -> None:
        self.db = db
        self.task_publisher = task_publisher

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
                task_sales = tg.create_task(self._get_sales_analytics(event_id))
                task_occupancy = tg.create_task(self._get_occupancy_analytics(event_id))
        except* Exception:
            logger.exception("Failed to get analytics from DB")
            raise DashboardUnavailableError()

        sales = task_sales.result()
        occupancy = task_occupancy.result()

        sales = self._build_sales_dashboard(sales)
        occupancy = self._build_occupancy_dashboard(occupancy)
        event_dashboard = EventDashboard(
            event_title=event.title,
            starts_at=event.starts_at,
            sales=sales,
            occupancy=occupancy
        )

        await self._schedule_event_report(event_id, event_dashboard)
        return event_dashboard

    async def _schedule_event_report(
            self,
            event_id: int,
            event_dashboard: EventDashboard
    ) -> None:
        async with self.db.transaction() as db:
            report_id = await db.reports.create_report(
                event_id=event_id,
                payload=event_dashboard.model_dump(mode="json")
            )
        if report_id:
            await self.task_publisher.schedule_event_dashboard_report(report_id)
        else:
            logger.error("Failed to add report metadata to database")
            return

    async def _get_sales_analytics(self, event_id: int) -> SalesRead:
        async with self.db.transaction() as db:
            sales = await db.bookings.get_sales(event_id)

        return sales

    async def _get_occupancy_analytics(self, event_id: int) -> OccupancyRead:
        async with self.db.transaction() as db:
            occupancy = await db.event_seats.get_occupancy(event_id)

        return occupancy


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
