from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

from afisha.api.dependencies import CurrentUserId
from afisha.application.dto import (
    BookingCreate,
    CheckoutResponse,
    EventData,
    EventSeatRead,
)
from afisha.services.booking import BookingService
from afisha.services.event import EventService

router = APIRouter(prefix="/events", route_class=DishkaRoute, tags=["Мероприятие"])


@router.get("/")
async def list_events() -> list[EventData]:
    """Возвращает список мероприятий для клиента."""
    ...


@router.get("/{event_id}")
async def get_event(event_id: int, service: FromDishka[EventService]) -> EventData:
    """Возвращает описание мероприятия."""
    return await service.get_event(event_id=event_id)


@router.get("/{event_id}/seats")
async def list_event_seats(event_id: int) -> list[EventSeatRead]:
    """Возвращает места на мероприятии с ценами и статусами."""
    ...


@router.post("/{event_id}/checkout")
async def prepare_checkout(
    event_id: int,
    payload: BookingCreate,
    user_id: CurrentUserId,
    service: FromDishka[BookingService]
) -> CheckoutResponse:
    """Временно бронирует места за клиентом, возвращает итоговую стоимость
        и возможность страховки."""
    return await service.reserve(
        event_id=event_id,
        payload=payload,
        user_id=user_id
    )
