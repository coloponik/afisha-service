from datetime import datetime, UTC, timedelta
from pathlib import Path

from afisha.application.dto import EventDashboard
from afisha.core.config import ReportConfig
from afisha.infrastructure.postgres.manager import DatabaseManager
from afisha.infrastructure.reports.pdf_reports import generate_event_dashboard_pdf
from afisha.infrastructure.tasks.publisher import TaskPublisher


class ReportService:
    def __init__(
            self,
            db: DatabaseManager,
            config: ReportConfig,
            task_publisher: TaskPublisher
    ) -> None:
        self.db = db
        self.storage_path = config.storage_path
        self.processing_timeout = timedelta(minutes=config.processing_timeout)
        self.pending_timeout = timedelta(minutes=config.pending_timeout)
        self.task_publisher = task_publisher

    async def generate_event_report(self, report_id: str) -> None:
        threshold = datetime.now(UTC) - self.processing_timeout

        report = await self.db.reports.claim_report(
            report_id=report_id,
            threshold=threshold
        )
        await self.db.commit()

        if report is None:
            return

        try:
            report_data = EventDashboard.model_validate(report.payload)
            output_path = Path(self.storage_path) / f"{report_id}.pdf"
            file_path = generate_event_dashboard_pdf(report_data, output_path)
            await self.db.reports.set_completed(report_id, str(file_path), report.claim_version)
            await self.db.commit()
        except Exception as exc:
            await self.db.reports.set_failed(report_id, str(exc), report.claim_version)
            await self.db.commit()
            raise

    async def recover_pending_reports(self) -> None:
        threshold = datetime.now(UTC) - self.pending_timeout

        reports_ids = await self.db.reports.get_stuck_pending(threshold)

        for report_id in reports_ids:
            await self.task_publisher.schedule_event_dashboard_report(report_id)
