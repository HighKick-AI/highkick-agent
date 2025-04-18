from datetime import datetime, timedelta, timezone
from typing import List

from fastapi import (
    APIRouter,
    status,
    Depends,
    Body
)
from fastapi import APIRouter, Depends, status, HTTPException, Response


from app.core.dependencies import get_settings, get_executor
from app.core.settings import AuthSettings
from app.schemas.account import AccountConsumeSchema
from app.schemas.auth import Token
from app.schemas.error import ErrorSchema
from app.service.executor import ExecutorService

import jwt
from passlib.context import CryptContext

router = APIRouter()

@router.post(
    "/script",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    name="accounts",
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ErrorSchema,
            "description": "Unknown error",
        },
    },
)
async def call_executor(
    script: str = Body(..., media_type="text/plain"),
    executor: ExecutorService = Depends(get_executor),
) -> dict:
    # TODO - substitute {{output_file}} name (RANDOM NAME)
    configured_script = executor.configure_script(script=script)
    executor.execute_script(script=configured_script)
    # TODO - read output-file to RAM
    # TODO - delete output-file

    # TODO return <<output file content>>
    return {"hello": configured_script}
