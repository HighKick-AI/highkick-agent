from datetime import datetime, timedelta, timezone
from typing import List

from fastapi import (
    APIRouter,
    status,
    Depends,
)
from fastapi import APIRouter, Depends, status, HTTPException, Response


from app.core.dependencies import get_settings, get_password_context
from app.core.settings import AuthSettings
from app.schemas.account import AccountConsumeSchema
from app.schemas.auth import Token
from app.schemas.error import ErrorSchema

import jwt
from passlib.context import CryptContext

router = APIRouter()

@router.post(
    "/",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    name="accounts",
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ErrorSchema,
            "description": "Unknown error",
        },
    },
)
async def create_account(
    account: AccountConsumeSchema,
    settings: AuthSettings = Depends(get_settings(AuthSettings)),
    pass_context: CryptContext = Depends(get_password_context),
) -> Token:
    return Token(access_token="test-token")




def create_access_token(
        account_id: str, 
        secret: str,
        algorithm: str,
        expires_delta: timedelta
) -> str:
    
    expire = datetime.now(timezone.utc) + expires_delta

    to_encode = {
        "sub": account_id,
        "exp": expire
    }

    encoded_jwt = jwt.encode(to_encode, key=secret, algorithm=algorithm)
    return encoded_jwt