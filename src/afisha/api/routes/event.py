from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

from afisha.api.dependencies import CurrentUserId
from afisha.application.dto import EventRead, EventSeatRead, BookingCreate, CheckoutResponse

router = APIRouter(prefix="/events", route_class=DishkaRoute, tags=["Мероприятие"])


@router.get("/")
async def list_events() -> list[EventRead]:
    """Возвращает список мероприятий для клиента."""
    ...


@router.get("/{event_id}")
async def get_event(event_id: int) -> EventRead:
    """Возвращает описание мероприятия."""
    ...


@router.get("/{event_id}/seats")
async def list_event_seats(event_id: int) -> list[EventSeatRead]:
    """Возвращает места на мероприятии с ценами и статусами."""
    ...


@router.post("/{event_id}/checkout")
async def prepare_checkout(
    event_id: int,
    payload: BookingCreate,
    user_id: CurrentUserId,
) -> CheckoutResponse:
    """Временно бронирует места за клиентом, возвращает итоговую стоимость
        и возможность страховки."""
    # TODO: создать бронь для выбранных мест через SELECT FOR UPDATE, и посчитать базовую стоимость.
    # TODO: конкурентно запросить Payment API и Protection API для расчета checkout.
    ...
