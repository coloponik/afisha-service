from collections.abc import Sequence
from typing import Any

from sqlalchemy import insert

from monitoring.infrastructure.postgres.models import EventPaymentActivity
from monitoring.infrastructure.postgres.repositories.base import BaseRepo


class EventPaymentActivityRepo(BaseRepo):
    async def create_many(self, rows: Sequence[dict[str, Any]]) -> None:
        if not rows:
            return

        stmt = insert(EventPaymentActivity).values(list(rows))
        await self.session.execute(stmt)
