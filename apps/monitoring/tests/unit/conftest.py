import asyncio
from datetime import datetime, UTC
from uuid import uuid4

import pytest
from unittest.mock import AsyncMock

from monitoring.infrastructure.websocket.manager import WebsocketManager, WebsocketClient
from monitoring.services.purchase_aggregation import (
    PurchaseAggregationService,
)


@pytest.fixture
def db_mock():
    return AsyncMock()


@pytest.fixture
def purchase_aggregation_service(
    db_mock,
) -> PurchaseAggregationService:
    return PurchaseAggregationService(db=db_mock)


@pytest.fixture
def websocket_manager() -> WebsocketManager:
    return WebsocketManager()


@pytest.fixture
def websocket_client_factory():
    def create_client() -> WebsocketClient:
        return WebsocketClient(
            ws=AsyncMock(),
            queue=asyncio.Queue(),
        )

    return create_client


@pytest.fixture
def fake_events():
    return [
            {
                "payment_id": str(uuid4()),
                "event_id": 1,
                "tickets_count": 2,
                "total_amount": 2000,
                "paid_at": datetime.now(UTC)
            },
            {
                "payment_id": str(uuid4()),
                "event_id": 1,
                "tickets_count": 3,
                "total_amount": 3500,
                "paid_at": datetime.now(UTC)
            },
            {
                "payment_id": str(uuid4()),
                "event_id": 2,
                "tickets_count": 1,
                "total_amount": 1000,
                "paid_at": datetime.now(UTC)
            },
    ]
