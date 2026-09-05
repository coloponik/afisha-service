import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import timedelta

from dishka import Scope

from afisha.core.container import create_container
from afisha.infrastructure.tasks.taskiq_app import broker_cpu
from afisha.main import settings
from afisha.services.booking import BookingService
from afisha.services.report import ReportService

logger = logging.getLogger(__name__)


@asynccontextmanager
async def get_task_service(service_type) -> AsyncIterator:
    container = create_container(settings)

    try:
        async with container(scope=Scope.REQUEST) as request_container:
            service = await request_container.get(service_type)
            yield service
    finally:
        await container.close()


@broker_cpu.task(
    task_name="generate_event_pdf_report",
    ack_type="when_executed",
    retry_on_error=True,
    max_retries=2
)
async def generate_event_pdf_report(report_id: str) -> None:
    container = create_container(settings)
    logger.info("Report started")
    async with container(scope=Scope.REQUEST) as request_container:
        service = await request_container.get(ReportService)
        await service.generate_event_report(report_id)
    logger.info("Report finished")


@broker_cpu.task(
    task_name="recover_pending_pdf_reports",
    schedule=[
        {
            "schedule_id": "recover_pending_pdf_reports-every-minute",
            "interval": timedelta(minutes=1)
        }
    ]
)
async def recover_pending_pdf_reports() -> None:
    container = create_container(settings)

    async with container(scope=Scope.REQUEST) as request_container:
        service = await request_container.get(ReportService)
        await service.recover_pending_reports()


@broker_cpu.task(
    task_name="cleanup_expired_bookings",
    schedule=[
        {
            "schedule_id": "cleanup_expired_bookings-every_minute",
            "interval": timedelta(minutes=1)
        }
    ]
)
async def cleanup_expired_bookings() -> None:
    async with get_task_service(BookingService) as service:
        await service.release_expired_bookings()
