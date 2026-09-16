from datetime import datetime, UTC
from uuid import UUID

from pydantic import BaseModel, field_validator, Field


class PurchaseEvent(BaseModel):
    payment_id: str
    event_id: int = Field(gt=0)
    tickets_count: int = Field(gt=0)
    total_amount: int = Field(gt=0)
    paid_at: datetime

    @field_validator("payment_id", mode="before")
    @classmethod
    def validate_payment_id(cls, value: str | UUID) -> str:
        return str(UUID(str(value)))

    @field_validator("paid_at")
    @classmethod
    def normalize_paid_at(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value
