from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CalculatedPaymentData(BaseModel):
    commission: int
    total: int
    payment_methods: list[str]
    expires_at: datetime | None = None

    model_config = ConfigDict(frozen=True)


class CalculatedProtectionData(BaseModel):
    available: bool
    price: int
    covered_amount: int
    description: str | None = None

    model_config = ConfigDict(frozen=True)
