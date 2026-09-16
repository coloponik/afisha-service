from pathlib import Path

from fastapi import FastAPI

from afisha.application.dto import EventDashboard
from afisha.enums import ReportStatus
from afisha.infrastructure.postgres.manager import DatabaseManager
from afisha.services.report import ReportService


class TestReportService:
    async def test_generate_event_report_succes(
            self,
            running_test_app: FastAPI,
            db: DatabaseManager,
            report_service: ReportService,
            fake_report_payload: EventDashboard
    ) -> None:
        report_id = await db.reports.create_report(
            1,
            fake_report_payload.model_dump(mode="json")
        )
        await db.commit()

        await report_service.generate_event_report(report_id)

        saved_report = await db.reports.get_report(report_id)

        file_path = Path(saved_report.file_path)

        assert saved_report.status == ReportStatus.COMPLETED
        assert file_path.parent == report_service.storage_path
        assert file_path.suffix == ".pdf"
        assert file_path.exists()
        assert file_path.stat().st_size > 0
