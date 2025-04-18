from fastapi import APIRouter

from app.routers.v1 import (
    accounts,
    agent
)

def provide_api_v1_router() -> APIRouter:
    router = APIRouter()
    router.include_router(accounts.router, prefix='/accounts', tags=['V1: accounts'])
    router.include_router(agent.router, prefix='/agent', tags=['V1: agaent'])
    return router
