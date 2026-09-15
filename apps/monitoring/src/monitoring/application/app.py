from dishka import AsyncContainer
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from monitoring.application.lifespan import create_lifespan


def create_fastapi_app(container: AsyncContainer) -> FastAPI:
    app = FastAPI(title="Сервис мониторинга", lifespan=create_lifespan(container))

    setup_dishka(container=container, app=app)
    
    return app
