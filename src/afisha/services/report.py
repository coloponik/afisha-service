from pathlib import Path

from afisha.application.dto import EventDashboard
from afisha.infrastructure.postgres.manager import DatabaseManager
from afisha.infrastructure.reports.pdf_reports import generate_event_dashboard_pdf


class ReportService:
    def __init__(self, db: DatabaseManager, storage_path: str) -> None:
        self.db = db
        self.storage_path = storage_path

    async def generate_event_report(self, report_id: str) -> None:
        report = await self.db.reports.get_report(report_id=report_id)

        if report is None:
            return

        await self.db.reports.set_processing(report_id)
        await self.db.commit()

        try:
            report_data = EventDashboard.model_validate(report.payload)
            output_path = Path(self.storage_path) / f"{report_id}.pdf"
            file_path = generate_event_dashboard_pdf(report_data, output_path)
            await self.db.reports.set_completed(report_id, str(file_path))
            await self.db.commit()
        except Exception as exc:
            await self.db.reports.set_failed(report_id, str(exc))
            await self.db.commit()
            raise


