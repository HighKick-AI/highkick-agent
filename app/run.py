import uvicorn

from app import settings

if __name__ == "__main__":
    uvicorn.run(
        app="app.setup:app",
        workers=settings.NUMBER_OF_WORKERS,
        host=settings.SERVICE_HOST,
        port=settings.SERVICE_PORT,
        reload=settings.RELOAD,
    )
