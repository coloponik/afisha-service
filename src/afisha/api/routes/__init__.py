from fastapi import APIRouter
from afisha.api.routes.routes import router as events_router

root_router = APIRouter()

root_router.include_router(events_router)
