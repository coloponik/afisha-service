import asyncio
import random
from datetime import datetime, UTC
from uuid import uuid4

from faststream.kafka import KafkaPublishMessage, KafkaBroker

from afisha.application.dto import PurchaseEvent
from afisha.core.config import KafkaConfig


class PurchaseSimulationService:
    def __init__(self, broker: KafkaBroker, config: KafkaConfig) -> None:
        self.broker = broker
        self.config = config
        self.publish_batch_size = 10

    async def run_simulation(self) -> None:
        while True:
            batch_size = random.randint(1, 30)

            events = [
                self._generate_purchase_event()
                for _ in range(batch_size)
            ]

            await self._publish_event_batch(events)

            await asyncio.sleep(random.randint(1, 3))

    def _generate_purchase_event(self) -> PurchaseEvent:
        purchase_event = PurchaseEvent(
            payment_id=str(uuid4()),
            event_id=random.randint(1, 5),
            tickets_count=random.randint(1, 5),
            total_amount=random.randint(1000, 40000),
            paid_at=datetime.now(UTC)
        )
        return purchase_event

    async def _publish_event_batch(self, events: list[PurchaseEvent]) -> None:
        for start in range(0, len(events), self.publish_batch_size):
            chunk = events[start: start + self.publish_batch_size]

            await self.broker.publish_batch(
                *[
                    KafkaPublishMessage(
                        body=event,
                        key=str(event.event_id).encode()
                    )
                    for event in chunk
                ],
                topic=self.config.purchase_topic
            )
