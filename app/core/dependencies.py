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
    S3Settings
)
from app.schemas.aws import ServiceName

import jwt
from jwt.exceptions import InvalidTokenError

from passlib.context import CryptContext

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


def _get_db_pool(request: HTTPConnection) -> AsyncEngine:
    return request.app.state.db_pool

async def get_session(
    pool: AsyncEngine = Depends(_get_db_pool),
) -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(pool, expire_on_commit=False) as session:
        yield session


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

# async def get_current_account(
#         token: HTTPAuthorizationCredentials = Depends(bearer_auth),
#         settings: AuthSettings = Depends(get_settings(AuthSettings)),
#         account_repo: AccountRepo = Depends(get_repo(AccountRepo)),
# ) -> Account:
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
#         user_id: str = payload.get("sub")
#         if user_id is None:
#             raise credentials_exception
#     except InvalidTokenError:
#         raise credentials_exception
#     account = await account_repo.get_by_id(user_id)
#     if account is None:
#         raise credentials_exception
#     return account

async def get_current_account(
        request: Request,
        settings: AuthSettings = Depends(get_settings(AuthSettings)),
        # account_repo: AccountRepo = Depends(get_repo(AccountRepo)),
) -> str:
    return "hello world"
