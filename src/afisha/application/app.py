from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from afisha.api.exception_handlers import setup_exception_handlers
from afisha.api.routes import root_router
from afisha.application.lifespan import lifespan
from afisha.core.config import Settings


def create_fastapi_app(settings: Settings, container) -> FastAPI:
    app = FastAPI(title="API Афиши", lifespan=lifespan, debug=False)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    setup_dishka(container=container, app=app)

    setup_exception_handlers(app)

    app.include_router(root_router)
    return app
