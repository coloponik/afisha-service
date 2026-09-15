import logging

import uvicorn

from monitoring.application.app import create_fastapi_app
from monitoring.core.config import Settings
from monitoring.core.container import create_container
from monitoring.core.logging_config import setup_logging

logger = logging.getLogger(__name__)

settings = Settings()

container = create_container(settings)
app = create_fastapi_app(container)

setup_logging()
logger.info(
    "Monitoring service is configured host=%s port=%s reload=%s",
    settings.app.host,
    settings.app.port,
    settings.app.reload
)

if __name__ == "__main__":
    uvicorn.run(
        "monitoring.main:app",
        host=settings.app.host,
        port=settings.app.port,
        reload=settings.app.reload,
        loop="uvloop"
    )
