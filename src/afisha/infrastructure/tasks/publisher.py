from afisha.application.dto import ProtectionRetryData


class TaskPublisher:
    async def schedule_event_dashboard_report(self, report_id: str) -> None:
        from afisha.infrastructure.tasks.taskiq_tasks import generate_event_pdf_report

        await generate_event_pdf_report.kiq(report_id)

    async def schedule_protection_retry(self, data: ProtectionRetryData) -> None:
        from afisha.infrastructure.tasks.taskiq_tasks import booking_protection_retry

        await booking_protection_retry.kiq(data.model_dump(mode="json"))
