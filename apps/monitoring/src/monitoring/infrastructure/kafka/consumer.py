from dishka import AsyncContainer, Scope
from faststream import AckPolicy
from faststream.kafka import KafkaBroker, KafkaMessage

from monitoring.core.config import KafkaConfig
from monitoring.infrastructure.kafka.schemas import PurchaseEvent
from monitoring.services.purchase_aggregation import PurchaseAggregationService


def create_kafka_broker(config: KafkaConfig, container: AsyncContainer) -> KafkaBroker:
    broker = KafkaBroker(
        bootstrap_servers=config.bootstrap_servers
    )

    @broker.subscriber(
        config.purchase_topic,
        batch=True,
        group_id=config.group_id,
        auto_offset_reset="earliest",
        ack_policy=AckPolicy.MANUAL,
        max_records=10,
        batch_timeout_ms=500
    )
    async def process_purchase_events(
            messages: list[PurchaseEvent],
            msg: KafkaMessage
    ) -> None:
        async with container(scope=Scope.REQUEST) as request_container:
            purchase_aggregation_service = await request_container.get(PurchaseAggregationService)
            await purchase_aggregation_service.process(messages)
            await msg.ack()

    return broker


