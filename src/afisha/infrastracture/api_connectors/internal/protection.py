from datetime import datetime

from afisha.infrastracture.api_connectors.base import BaseHTTPConnector
from afisha.infrastracture.api_connectors.schemas import CalculatedProtectionData


class ProtectionConnector(BaseHTTPConnector):
    async def get_protection_info(
            self,
            booking_id: int,
            ticket_amount: int,
            event_category: str,
            event_starts_at: datetime
    ) -> CalculatedProtectionData:
        response = await self._request(
            "POST",
            "/protection/calculate",
            retry=True,
            json={
                "booking_id": booking_id,
                "ticket_amount": ticket_amount,
                "event_category": event_category,
                "event_starts_at": event_starts_at
            }
        )
        response.raise_for_status()

        return CalculatedProtectionData.model_validate(response.json())
