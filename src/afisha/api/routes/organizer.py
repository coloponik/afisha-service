from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

from afisha.api.dependencies import CurrentUserId
from afisha.application.dto import EventCreate, EventDashboard, EventRead
from afisha.services.event_analytics import EventAnalyticsService

router = APIRouter(prefix="/organizer", route_class=DishkaRoute, tags=["Организатор"])


@router.get("/events")
async def list_organizer_events(organizer_id: CurrentUserId) -> list[EventRead]:
    """Возвращает список созданных событий текущего организатора."""
    ...


@router.post("/events")
async def create_event(payload: EventCreate, organizer_id: CurrentUserId) -> EventRead:
    """Создает мероприятие от лица текущего организатора."""
    ...


@router.get("/events/{event_id}/dashboard")
async def get_event_dashboard(
        event_id: int,
        organizer_id: CurrentUserId,
        service: FromDishka[EventAnalyticsService]
) -> EventDashboard:
    """Возвращает аналитические данные для дашборда по мероприятию."""
    return await service.get_dashboard(
        event_id=event_id,
        organizer_id=organizer_id
    )
