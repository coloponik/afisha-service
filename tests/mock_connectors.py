from datetime import datetime

from afisha.infrastracture.api_connectors.schemas import CalculatedPaymentData, \
    CalculatedProtectionData


class MockPaymentConnector:
    async def get_commission(
            self,
            booking_id: int,
            amount: int,
            currency: str
    ):
        return CalculatedPaymentData(
            commission=10,
            total=amount + 10,
            payment_methods=["bank_card", "sbp"],
            expires_at=None
        )


class MockProtectionConnector:
    async def get_protection_info(
            self,
            booking_id: int,
            ticket_amount: int,
            event_category: str,
            event_starts_at: datetime
    ):
        return CalculatedProtectionData(
            available=False,
            price=50,
            covered_amount=0,
            description=None
        )
