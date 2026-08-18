from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

from afisha.api.dependencies import CurrentUserId
from afisha.application.dto import PaymentCompleted, PaymentCreate

router = APIRouter(prefix="/bookings", route_class=DishkaRoute, tags=["Оплата"])


@router.post("/{booking_id}/pay")
async def pay_booking(
    booking_id: int,
    payload: PaymentCreate,
    user_id: CurrentUserId,
) -> PaymentCompleted:
    """Принимает способ оплаты и флаг with_protection."""
    ...
