from subprocess import TimeoutExpired
import uuid
from datetime import datetime, timedelta, timezone
from typing import List
import json
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
from fastapi.concurrency import run_in_threadpool


from app.core.task_pool import AsyncTaskPool
from app.core.dependencies import get_settings, get_executor, get_auth_access, get_task_pool
from app.core.agent_job import AgentJob
from app.core.exceptions import NotFoundException
from app.core.settings import AuthSettings
from app.schemas.agent import JobProduceSchema, StatusSchema
from app.schemas.error import ErrorSchema
from app.service.executor import ExecutorService

import jwt
from passlib.context import CryptContext

router = APIRouter()

@router.post(
    "/jobs",
    response_model=JobProduceSchema,
    status_code=status.HTTP_200_OK,
    name="accounts",
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ErrorSchema,
            "description": "Unknown error",
        },
    },
)
async def start_job(
    script: str = Body(..., media_type="text/plain"),
    executor: ExecutorService = Depends(get_executor),
    task_pool: AsyncTaskPool = Depends(get_task_pool),
    auth: dict = Depends(get_auth_access),
) -> JobProduceSchema:
    
    job = AgentJob(base_dir=executor.get_output_dir(), id=str(uuid.uuid4()))
    job.set_status(StatusSchema())

    task_pool.add_task(
        run_job,
        job=job,
        executor=executor,
        script=script
    )    
    
    return JobProduceSchema(id=job.get_id())


async def run_job(job: AgentJob, executor: ExecutorService, script: str):
    
    configured_script = executor.configure_script(script=script, output_file_path=job.get_data_path_str())

    status = StatusSchema()
    status.time_started = datetime.now()
    job.set_status(status)

    try:
        std_out, err = await run_in_threadpool(
            executor.execute_script,
            script=configured_script["script"]
        )
    except TimeoutExpired as e:
        std_out = ""
        err = f"Timeout expired after {e.timeout} seconds"

    finally:
        pass

    status.time_completed = datetime.now()
    status.error = not (not err or err.strip() == "")

    job.set_std_output(std_out)
    job.set_error(err)        

    job.set_status(status)


@router.get(
    "/jobs/{job_id}/status",
    response_model=StatusSchema,
    status_code=status.HTTP_200_OK,
    name="Get job status",
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ErrorSchema,
            "description": "Unknown error",
        },
    },
)
async def get_job_status(
    job_id: str,
    executor: ExecutorService = Depends(get_executor),
    auth: dict = Depends(get_auth_access),
) -> StatusSchema:
    job = AgentJob(base_dir=executor.get_output_dir(), id=job_id)
    status = job.get_status()
    if status is None:
        raise NotFoundException()
    return status


@router.get(
    "/jobs/{job_id}/data",
    status_code=status.HTTP_200_OK,
    name="Get output data",
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ErrorSchema,
            "description": "Unknown error",
        },
    },
)
async def get_job_data(
    job_id: str,
    executor: ExecutorService = Depends(get_executor),
    auth: dict = Depends(get_auth_access),
) -> StreamingResponse:
    job = AgentJob(base_dir=executor.get_output_dir(), id=job_id)
    path = job.get_data_path()
    if path is None:
        raise NotFoundException()
    
    file_stream = open(path, mode="rb")
    return StreamingResponse(file_stream, media_type="application/json")



@router.get(
    "/jobs/{job_id}/std-output",
    status_code=status.HTTP_200_OK,
    name="Get std output",
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ErrorSchema,
            "description": "Unknown error",
        },
    },
)
async def get_std_output(
    job_id: str,
    executor: ExecutorService = Depends(get_executor),
    auth: dict = Depends(get_auth_access),
) -> StreamingResponse:
    job = AgentJob(base_dir=executor.get_output_dir(), id=job_id)
    path = job.get_std_output_path()
    if path is None:
        raise NotFoundException()
    
    file_stream = open(path, mode="rb")
    return StreamingResponse(file_stream, media_type="text/plain")
    


@router.get(
    "/jobs/{job_id}/error",
    status_code=status.HTTP_200_OK,
    name="Get error",
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ErrorSchema,
            "description": "Unknown error",
        },
    },
)
async def get_error(
    job_id: str,
    executor: ExecutorService = Depends(get_executor),
    auth: dict = Depends(get_auth_access),
) -> StreamingResponse:
    job = AgentJob(base_dir=executor.get_output_dir(), id=job_id)
    path = job.get_error_path()
    if path is None:
        raise NotFoundException()
    
    file_stream = open(path, mode="rb")
    return StreamingResponse(file_stream, media_type="text/plain")
    