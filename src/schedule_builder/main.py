from contextlib import asynccontextmanager

from fastapi import FastAPI

from schedule_builder.api.router import api_router
from schedule_builder.config.settings import settings
from schedule_builder.core.exceptions import register_exception_handlers
from schedule_builder.core.logging import configure_logging, get_logger
from schedule_builder.core.middleware import RequestLoggingMiddleware

configure_logging(settings.log_level, settings.log_format)
logger = get_logger("schedule_builder.main")


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info(
        "Application startup: env=%s debug=%s",
        settings.environment,
        settings.debug,
    )
    yield
    logger.info("Application shutdown complete")


app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    docs_url=settings.api_docs_url,
    redoc_url=settings.api_redoc_url,
    openapi_url=settings.api_openapi_url,
    lifespan=lifespan,
)

app.add_middleware(RequestLoggingMiddleware)
register_exception_handlers(app)

app.include_router(api_router)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Schedule Builder API"}
