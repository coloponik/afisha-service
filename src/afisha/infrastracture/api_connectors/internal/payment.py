from afisha.infrastracture.api_connectors.base import BaseHTTPConnector
from afisha.infrastracture.api_connectors.schemas import CalculatedPaymentData


class PaymentConnector(BaseHTTPConnector):
    async def get_commission(
            self,
            booking_id: int,
            amount: int,
            currency: str
    ) -> CalculatedPaymentData:
        response = await self._request(
            "POST",
            "/payment/calculate",
            retry=True,
            json={
                "booking_id": booking_id,
                "amount": amount,
                "currency": currency
            }
        )
        response.raise_for_status()

        return CalculatedPaymentData.model_validate(response.json())

