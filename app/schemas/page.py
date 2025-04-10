
from typing import Optional, List, Any
from uuid import UUID
from app.schemas.base import BaseSchema

class PageProduceSchema (BaseSchema):
    total: int
    offset: int
    limit: int
    items: List[Any]
