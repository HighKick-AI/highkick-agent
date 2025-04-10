from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

from app.core.settings import Settings
from app.routers import system
from app.routers.v1 import provide_api_v1_router
from app.schemas.error import ErrorSchema


def provide_app(settings: Settings) -> FastAPI:
    app = FastAPI(
        title=settings.SERVICE_NAME,
        debug=settings.DEBUG,
        version=settings.SERVICE_VERSION,
        responses={
            status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ErrorSchema}
        },
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.state.settings = settings

    app.include_router(system.router)

    api_v1_router = provide_api_v1_router()
    app.include_router(api_v1_router, prefix="/api/v1")

    return app


settings = Settings()
app = provide_app(settings)
