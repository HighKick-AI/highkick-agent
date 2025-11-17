from typing import (
    TYPE_CHECKING,
    Any,
    AsyncGenerator,
    Callable,
    Type,
    TypeVar,
)

import boto3
from fastapi import Depends, HTTPException, Security, FastAPI, status
from fastapi.requests import Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from starlette.requests import HTTPConnection
import yaml

from app.clients import BedrockClient, S3Client
from app.clients.aws import AWSClient

from app.core.exceptions import (
    BadCredentialsException,
    RequiresAuthenticationException,
)
from app.core.settings import (
    AuthSettings,
    AWSSettings,
    BedrockClientSettings,
    S3Settings,
    AgentConfig
)
from app.schemas.aws import ServiceName
from app.service.executor import ExecutorService

import jwt
from jwt.exceptions import InvalidTokenError

from passlib.context import CryptContext

from core.task_pool import AsyncTaskPool

if TYPE_CHECKING:
    from types_aiobotocore_s3 import S3Client as S3ClientBoto

T = TypeVar("T")


def get_settings(setting_type: type[T]) -> Callable[[Request], T]:
    def dependency(request: Request) -> T:
        for attr_name in request.app.state.settings.__dict__:
            attr = getattr(request.app.state.settings, attr_name)

            if isinstance(attr, setting_type):
                return attr

        raise ValueError(
            f"Setting of type {setting_type} not found in app settings."
        )

    return dependency

def get_executor(
    agent_config: AgentConfig = Depends(get_settings(AgentConfig)),
) -> ExecutorService:
    return ExecutorService(agent_config=agent_config)

def get_task_pool(request: HTTPConnection) -> AsyncTaskPool:
    return request.app.state.task_pool

def get_aws_client(service_name: ServiceName, **kwargs: Any) -> Callable:
    async def _get_client(request: Request) -> AsyncGenerator:
        async with AWSClient(
            service_name=service_name,
            settings=request.app.state.settings.aws,
            **kwargs,
        ).session() as client:
            yield client

    return _get_client

def get_s3_client(
    settings: S3Settings = Depends(get_settings(S3Settings)),
    s3_client: "S3ClientBoto" = Depends(get_aws_client(service_name="s3")),
) -> S3Client:
    return S3Client(s3_client=s3_client, settings=settings)


def get_bedrock_client(
    settings: BedrockClientSettings = Depends(
        get_settings(BedrockClientSettings)
    ),
) -> BedrockClient:
    boto_client_agent = boto3.client(
        "bedrock-agent", region_name=settings.REGION_NAME
    )
    boto_client_agent_runtime = boto3.client(
        "bedrock-agent-runtime", region_name=settings.REGION_NAME
    )
    boto_client_runtime = boto3.client(
        "bedrock-runtime", region_name=settings.REGION_NAME
    )
    return BedrockClient(
        client_agent=boto_client_agent,
        client_agent_runtime=boto_client_agent_runtime,
        client_runtime=boto_client_runtime,
        bedrock_settings=settings,
    )


password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_context():
    return password_context


bearer_auth = HTTPBearer()

def _load_config(path: str):
    with open(path, "r") as f:
        config = yaml.safe_load(f)
    return config


async def get_config_yaml(
        agent_config: AgentConfig = Depends(get_settings(AgentConfig)),
) -> dict:
    return _load_config(agent_config.CONFIG_PATH)


async def get_auth_access(
        token: HTTPAuthorizationCredentials = Depends(bearer_auth),
        settings: AuthSettings = Depends(get_settings(AuthSettings)),
        agent_config: AgentConfig = Depends(get_settings(AgentConfig)),
) -> dict:
    
    config_yaml = _load_config(agent_config.CONFIG_PATH)
    secret = config_yaml["secrets"]["access"]

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        jwt.decode(token.credentials, secret, algorithms=[settings.ALGORITHM])
    except InvalidTokenError:
        raise credentials_exception
    return {
        "access": config_yaml["secrets"]["access"],
        "service": config_yaml["secrets"]["service"]
    }
