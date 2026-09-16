from fastapi import APIRouter

__all__ = ("root_router",)

from monitoring.api.routes.ws_purchase_events import purchase_events_router

root_router = APIRouter()

root_router.include_router(purchase_events_router)
