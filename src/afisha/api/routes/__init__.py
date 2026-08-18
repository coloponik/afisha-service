from fastapi import APIRouter

from afisha.api.routes.booking import router as booking_router
from afisha.api.routes.event import router as event_router
from afisha.api.routes.location import router as location_router
from afisha.api.routes.organizer import router as organizer_router

__all__ = ("root_router",)

root_router = APIRouter()

root_router.include_router(booking_router)
root_router.include_router(event_router)
root_router.include_router(location_router)
root_router.include_router(organizer_router)