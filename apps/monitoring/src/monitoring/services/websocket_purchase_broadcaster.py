from monitoring.infrastructure.queues.purchase_aggregates import PurchaseAggregatesQueue
from monitoring.infrastructure.websocket.manager import WebsocketManager


class WebSocketPurchaseBroadcaster:
    def __init__(
            self,
            ws_manager: WebsocketManager,
            queue: PurchaseAggregatesQueue,
    ) -> None:
        self.ws_manager = ws_manager
        self.queue = queue

    async def run(self) -> None:
        while True:
            aggregates = await self.queue.get()

            try:
                await self.ws_manager.broadcast(aggregates)
            finally:
                self.queue.task_done()
