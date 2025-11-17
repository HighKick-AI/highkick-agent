from datetime import datetime
from typing import Optional
from app.schemas.base import BaseSchema
from pydantic import field_serializer


class StatusSchema(BaseSchema):
    time_started: Optional[datetime] = None
    time_completed: Optional[datetime] = None
    error: bool = False

    @field_serializer("time_started", "time_completed")
    def serialize_dt(self, value: Optional[datetime], _info):
        return value.isoformat() if value else None


class JobProduceSchema(BaseSchema):
    id: str
