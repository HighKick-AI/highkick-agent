from typing import Any

from app.schemas.base import BaseSchema


class ErrorSchema(BaseSchema):
    errors: list[Any]
