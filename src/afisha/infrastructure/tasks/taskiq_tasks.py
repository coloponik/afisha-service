import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import timedelta

from dishka import Scope

from afisha.application.dto import ProtectionRetryData
from afisha.core.container import create_container
from afisha.infrastructure.tasks.taskiq_app import broker_cpu
from afisha.main import settings
from afisha.services.booking import BookingService
from afisha.services.report import ReportService

logger = logging.getLogger(__name__)


@asynccontextmanager
async def get_task_service[T](service_type: type[T]) -> AsyncIterator[T]:
    container = create_container(settings)

    try:
        async with container(scope=Scope.REQUEST) as request_container:
            service = await request_container.get(service_type)
            yield service
    finally:
        await container.close()


@broker_cpu.task(
    task_name="booking_protection_retry",
    ack_type="when_executed",
    retry_on_error=True,
    max_retries=1
)
async def booking_protection_retry(payload: dict) -> None:
    retry_data = ProtectionRetryData.model_validate(payload)

    async with get_task_service(BookingService) as service:
        await service.fetch_and_save_protection(retry_data)


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
    logger.info("Expired bookings cleaned up")


@broker_cpu.task(
    task_name="generate_event_pdf_report",
    ack_type="when_executed",
    retry_on_error=True,
    max_retries=2
)
async def generate_event_pdf_report(report_id: str) -> None:
    logger.info("Report started")
    async with get_task_service(ReportService) as service:
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
    async with get_task_service(ReportService) as service:
        await service.recover_pending_reports()
    logger.info("Stuck pending reports recovered")

