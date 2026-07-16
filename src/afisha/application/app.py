from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from afisha.api.routes import root_router
from afisha.application.lifespan import lifespan
from afisha.core.config import Settings


def create_fastapi_app(settings: Settings) -> FastAPI:
    app = FastAPI(title="API Афиши", lifespan=lifespan, debug=False)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(root_router)
    return app
