from enum import Enum

from app.schemas.base import BaseSchema


class IngestionStatus(str, Enum):
    STARTING = "STARTING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"
    STOPPING = "STOPPING"
    STOPPED = "STOPPED"

    @classmethod
    def is_terminal_state(cls, status: str) -> bool:
        return status in {
            cls.COMPLETE.value,
            cls.FAILED.value,
            cls.STOPPED.value,
        }


class IngestionJob(BaseSchema):
    ingestionJobId: str
    failureReasons: list[str] = []
    status: IngestionStatus


class IngestionJobResponse(BaseSchema):
    ingestionJob: IngestionJob
