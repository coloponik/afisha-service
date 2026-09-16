from dishka import AsyncContainer
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from monitoring.api.routes import root_router
from monitoring.application.lifespan import create_lifespan


def create_fastapi_app(container: AsyncContainer) -> FastAPI:
    app = FastAPI(title="Сервис мониторинга", lifespan=create_lifespan(container))

    setup_dishka(container=container, app=app)

    app.include_router(root_router)

    return app
