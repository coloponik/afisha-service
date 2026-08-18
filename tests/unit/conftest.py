from unittest.mock import MagicMock

import pytest

from afisha.services.event import EventService


@pytest.fixture
def event_service() -> EventService:
    db = MagicMock()
    cache = MagicMock()
    queue = MagicMock()

    return EventService(
        db=db,
        cache=cache,
        queue=queue,
    )
