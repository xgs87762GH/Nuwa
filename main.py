import uvicorn
from fastapi import FastAPI

from src.api.main import init_router
from src.core.config import get_logger, get_app_config

LOGGER = get_logger()
app_config = get_app_config()


def create_app() -> FastAPI:
    return init_router()


# 供 uvicorn 加载的应用实例
app = create_app()

if __name__ == "__main__":
    LOGGER.info("Starting application")
    uvicorn.run(app, host=app_config.host, port=app_config.port)
