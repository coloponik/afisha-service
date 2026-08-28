import logging

from dishka import Scope

from afisha.core.container import create_container
from afisha.infrastructure.tasks.taskiq_app import broker_cpu
from afisha.main import settings
from afisha.services.report import ReportService

logger = logging.getLogger(__name__)


@broker_cpu.task(
    task_name="generate_event_pdf_report",
    retry_on_error=True,
    max_retries=2
)
async def generate_event_pdf_report(report_id: str) -> None:
    container = create_container(settings)
    print("Container created")
    logger.info("Report started")
    async with container(scope=Scope.REQUEST) as request_container:
        service = await request_container.get(ReportService)
        print("Container gotten")
        await service.generate_event_report(report_id)
    print("Task finished")
    logger.info("Report finished")
