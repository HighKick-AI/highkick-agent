from datetime import datetime, timedelta, timezone
from typing import List

from fastapi import (
    APIRouter,
    status,
    Depends,
)
from fastapi import APIRouter, Depends, status, HTTPException, Response

from app.core.dependencies import get_settings, get_config_yaml
from app.core.settings import AuthSettings
from app.schemas.account import AccountConsumeSchema
from app.schemas.auth import AccessToken, ServiceToken
from app.schemas.error import ErrorSchema

import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext

router = APIRouter()

@router.get(
    "/debug/service-token",
    response_model=ServiceToken,
    status_code=status.HTTP_200_OK,
    name="generate debug service token",
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ErrorSchema,
            "description": "Unknown error",
        },
    },
)
async def create_debug_service_token(
    settings: AuthSettings = Depends(get_settings(AuthSettings)),
    config_yaml: dict = Depends(get_config_yaml),
) -> ServiceToken:
    
    token = ServiceToken(
        service_token=create_token(
            secret=config_yaml["secrets"]["service"],
            algorithm=settings.ALGORITHM,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
    )
    return token


@router.post(
    "/token",
    response_model=AccessToken,
    status_code=status.HTTP_200_OK,
    name="get access token",
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ErrorSchema,
            "description": "Unknown error",
        },
    },
)
async def create_access_token(
    token: ServiceToken,
    settings: AuthSettings = Depends(get_settings(AuthSettings)),
    config_yaml: dict = Depends(get_config_yaml),
) -> AccessToken:
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        jwt.decode(token.service_token, config_yaml["secrets"]["service"], algorithms=[settings.ALGORITHM])
    except InvalidTokenError:
        raise credentials_exception

    token = AccessToken(
        access_token=create_token(
            secret=config_yaml["secrets"]["access"],
            algorithm=settings.ALGORITHM,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
    )
    return token


def create_token(
        secret: str,
        algorithm: str,
        expires_delta: timedelta
) -> str:
    
    expire = datetime.now(timezone.utc) + expires_delta

    to_encode = {
        "exp": expire
    }

    encoded_jwt = jwt.encode(to_encode, key=secret, algorithm=algorithm)
    return encoded_jwt