from typing import Any
from uuid import uuid4

from monitoring.infrastructure.postgres.manager import DatabaseManager


class PurchaseAggregationService:
    def __init__(self, db: DatabaseManager) -> None:
        self.db = db

    async def process(self, events: list[Any]) -> None:
        event_aggregates = self._prepare_event_aggregates(events)

        if not event_aggregates:
            return

        await self._store_event_aggregates(event_aggregates)

    def _prepare_event_aggregates(
            self,
            events: list[Any]
    ) -> list[dict[str, Any]]:
        return self._aggregate_events(
            [self._build_purchase_event(event) for event in events]
        )

    def _build_purchase_event(self, event: Any) -> dict[str, Any]:
        return {
            "payment_id": event.payment_id,
            "event_id": event.event_id,
            "tickets_count": event.tickets_count,
            "total_amount": event.total_amount,
            "paid_at": event.paid_at
        }

    def _aggregate_events(
            self,
            purchase_events: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        batch_id = str(uuid4())
        event_aggregates: dict[int, dict[str, Any]] = {}

        for event in purchase_events:
            event_id = event["event_id"]

            aggregate = event_aggregates.setdefault(
                event_id,
                {
                    "batch_id": batch_id,
                    "event_id": event_id,
                    "payments_count": 0,
                    "tickets_count": 0,
                    "total_amount": 0,
                },
            )

            aggregate["payments_count"] += 1
            aggregate["tickets_count"] += event["tickets_count"]
            aggregate["total_amount"] += event["total_amount"]

        return list(event_aggregates.values())

    async def _store_event_aggregates(
            self,
            event_aggregates: list[dict[str, Any]]
    ) -> None:
        await self.db.event_payment_activities.create_many(event_aggregates)
        await self.db.commit()
