from datetime import datetime, timedelta, timezone
from typing import List
import os
import shutil

from fastapi import (
    APIRouter,
    status,
    Depends,
    Body
)
from fastapi.responses import StreamingResponse
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
) -> StreamingResponse:
    
    configured_script = executor.configure_script(script=script)

    print(configured_script)

    executor.execute_script(script=configured_script["script"])
    
    output_file = configured_script["output_file"]

    # spark_data_to_file(output_dir, output_file)

    file_stream = open(output_file, mode="rb")

    return StreamingResponse(file_stream, media_type="application/json")


def spark_data_to_file(output_dir: str, output_file: str):

    for filename in os.listdir(output_dir):
        if filename.startswith("part-") and filename.endswith(".json"):
            part_file = os.path.join(output_dir, filename)
            shutil.move(part_file, output_file)
            break

    shutil.rmtree(output_dir, ignore_errors=True)