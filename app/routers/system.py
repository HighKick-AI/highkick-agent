from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import JSONResponse

from app.core.dependencies import get_settings
from app.core.settings import GitSettings

router = APIRouter()


@router.get("/health")
async def health(
    settings: GitSettings = Depends(get_settings(GitSettings)),
) -> Response:
    response_content = {
        f"GIT_{key.upper()}": value
        for key, value in settings.model_dump().items()
    }

    return JSONResponse(
        content=response_content, status_code=status.HTTP_200_OK
    )
