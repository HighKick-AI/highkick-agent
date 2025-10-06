from fastapi import APIRouter

from app.routers.v1 import (
    agent,
    auth
)

def provide_api_v1_router() -> APIRouter:
    router = APIRouter()
    router.include_router(auth.router, prefix='/auth', tags=['V1: auth'])
    router.include_router(agent.router, prefix='/agent', tags=['V1: agaent'])
    return router
