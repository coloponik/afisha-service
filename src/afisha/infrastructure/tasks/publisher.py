

class TaskPublisher:
    async def schedule_event_dashboard_report(self, report_id: str) -> None:
        from afisha.infrastructure.tasks.taskiq_tasks import generate_event_pdf_report

        await generate_event_pdf_report.kiq(report_id)
