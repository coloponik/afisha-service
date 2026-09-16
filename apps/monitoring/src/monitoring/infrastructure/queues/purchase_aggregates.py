from asyncio import Queue
from typing import Any


class PurchaseAggregatesQueue:
    def __init__(self) -> None:
        self._queue: Queue[list[dict[str, Any]]] = Queue()

    async def put(self, aggregates: list[dict[str, Any]]) -> None:
        await self._queue.put(aggregates)

    async def get(self) -> list[dict[str, Any]]:
        return await self._queue.get()

    def task_done(self) -> None:
        self._queue.task_done()
