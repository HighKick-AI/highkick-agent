from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

import aioboto3

from app.core.settings import AWSSettings
from app.schemas.aws import Credentials, ServiceName


class AWSBase(ABC):
    def __init__(
        self, service_name: ServiceName, settings: AWSSettings, **kwargs: Any
    ) -> None:
        self.settings = settings
        self.service_name: str = service_name
        self.kwargs: dict[str, Any] = kwargs

    @property
    def credentials(self) -> Credentials:
        aws_credentials: Credentials = {
            "service_name": self.service_name,
            "region_name": self.settings.REGION_NAME,
            **self.kwargs,  # type: ignore
        }

        return aws_credentials

    @abstractmethod  # type: ignore
    @asynccontextmanager
    async def session(
        self,
    ) -> AsyncIterator[Any]:
        pass


class AWSClient(AWSBase):
    @asynccontextmanager
    async def session(self) -> AsyncIterator[Any]:  # type: ignore
        session = aioboto3.Session()
        async with session.client(  # type: ignore
            **self.credentials
        ) as client:
            yield client
