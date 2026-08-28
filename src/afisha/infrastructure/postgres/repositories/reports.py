from datetime import datetime, UTC
from uuid import uuid4

from sqlalchemy import select, update, insert

from afisha.application.dto import ReportData
from afisha.enums import ReportStatus
from afisha.infrastructure.postgres.models import Report
from afisha.infrastructure.postgres.repositories.base import BaseRepo


class ReportRepo(BaseRepo):
    async def create_report(self, event_id: int, payload: dict) -> str:
        report_id = str(uuid4())

        stmt = (
            insert(Report)
            .values(
                id=report_id,
                event_id=event_id,
                status=ReportStatus.PENDING,
                payload=payload
            )
        )

        await self.session.execute(stmt)
        return report_id

    async def get_report(self, report_id: str) -> ReportData | None:
        query = (
            select(Report)
            .where(Report.id == report_id)
        )

        result = await self.session.scalar(query)

        if result is None:
            return None

        return ReportData.model_validate(result)

    async def set_completed(self, report_id: str, file_path: str) -> None:
        now = datetime.now(UTC)
        stmt = (
            update(Report)
            .where(Report.id == report_id)
            .values(
                status=ReportStatus.COMPLETED,
                file_path=file_path,
                updated_at=now,
                completed_at=now,
                error=None
            )
        )

        await self.session.execute(stmt)

    async def set_failed(self, report_id: str, error: str) -> None:
        stmt = (
            update(Report)
            .where(Report.id == report_id)
            .values(
                status=ReportStatus.FAILED,
                updated_at=datetime.now(UTC),
                error=error
            )
        )

        await self.session.execute(stmt)

    async def set_processing(self, report_id: str) -> None:
        stmt = (
            update(Report)
            .where(Report.id == report_id)
            .values(
                status=ReportStatus.PROCESSING,
                updated_at=datetime.now(UTC),
                error=None
            )
        )

        await self.session.execute(stmt)
