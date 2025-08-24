import sys
from contextlib import asynccontextmanager
from logging import getLogger
from pathlib import Path

import uvicorn

from src.api.main import init_router
from src.core.config import (get_logger, get_app_config)

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# create the FastAPI app
app = init_router()

LOGGER = get_logger()

if __name__ == '__main__':
    LOGGER.info("Starting application")
    appConfig = get_app_config()
    uvicorn.run(app, host=appConfig.host, port=appConfig.port)
