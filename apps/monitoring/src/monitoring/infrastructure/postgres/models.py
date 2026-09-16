from datetime import datetime

from sqlalchemy import DateTime, text, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class EventPaymentActivity(Base):
    __tablename__ = "event_payment_activity"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    batch_id: Mapped[str] = mapped_column(String(36))
    event_id: Mapped[int]
    payments_count: Mapped[int]
    tickets_count: Mapped[int]
    total_amount: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
    )
