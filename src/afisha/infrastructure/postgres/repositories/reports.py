from datetime import datetime, UTC
from uuid import uuid4

from sqlalchemy import update, insert, or_, and_, select

from afisha.application.dto import ReportData
from afisha.enums import ReportStatus
from afisha.infrastructure.postgres.models import Report
from afisha.infrastructure.postgres.repositories.base import BaseRepo


class ReportRepo(BaseRepo):
    async def claim_report(
            self,
            report_id: str,
            threshold: datetime
    ) -> ReportData | None:
        stmt = (
            update(Report)
            .where(
                Report.id == report_id,
                or_(
                    Report.status == ReportStatus.PENDING,
                    Report.status == ReportStatus.FAILED,
                    and_(
                        Report.status == ReportStatus.PROCESSING,
                        Report.updated_at < threshold
                    )
                )
            )
            .values(
                status=ReportStatus.PROCESSING,
                claim_version=Report.claim_version + 1,
                updated_at=datetime.now(UTC)
            )
            .returning(Report)
        )

        result = await self.session.execute(stmt)
        report = result.scalar_one_or_none()

        return ReportData.model_validate(report) if report else None

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

    async def get_stuck_pending(self, threshold: datetime) -> list[str]:
        query = (
            select(Report.id)
            .where(
                Report.status == ReportStatus.PENDING,
                Report.created_at < threshold
            )
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def set_completed(self, report_id: str, file_path: str, claim_version: int) -> None:
        timestamp = datetime.now(UTC)

        stmt = (
            update(Report)
            .where(
                Report.id == report_id,
                Report.status == ReportStatus.PROCESSING,
                Report.claim_version == claim_version,
            )
            .values(
                status=ReportStatus.COMPLETED,
                file_path=file_path,
                updated_at=timestamp,
                completed_at=timestamp,
                error=None
            )
        )

        await self.session.execute(stmt)

    async def set_failed(self, report_id: str, error: str, claim_version: int) -> None:
        stmt = (
            update(Report)
            .where(
                Report.id == report_id,
                Report.status == ReportStatus.PROCESSING,
                Report.claim_version == claim_version,
            )
            .values(
                status=ReportStatus.FAILED,
                updated_at=datetime.now(UTC),
                error=error
            )
        )

        await self.session.execute(stmt)

    async def get_report(self, report_id: str) -> ReportData | None:
        query = (
            select(Report)
            .where(Report.id == report_id)
        )

        result = await self.session.scalar(query)

        if result is None:
            return None

        return ReportData.model_validate(result)

    # async def set_processing(self, report_id: str) -> None:
    #     stmt = (
    #         update(Report)
    #         .where(Report.id == report_id)
    #         .values(
    #             status=ReportStatus.PROCESSING,
    #             updated_at=datetime.now(UTC),
    #             error=None
    #         )
    #     )
    #
    #     await self.session.execute(stmt)
