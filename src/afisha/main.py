import logging
import uvicorn

from afisha.application.app import create_fastapi_app
from afisha.core.config import Settings
from afisha.core.container import create_container
from afisha.core.logging_config import setup_logging


logger = logging.getLogger(__name__)

settings = Settings()

setup_logging()
logger.info(
    "Afisha service is configured host=%s port=%s reload=%s",
    settings.app.host,
    settings.app.port,
    settings.app.reload
)

container = create_container(settings)
app = create_fastapi_app(settings, container)

if __name__ == "__main__":
    uvicorn.run(
        "afisha.main:app",
        host=settings.app.host,
        port=settings.app.port,
        reload=settings.app.reload,
        loop="uvloop",
    )
