from uuid import UUID

from app.schemas.base import BaseSchema

class AccountConsumeSchema (BaseSchema):
    email: str
    password: str

class AccountProduceSchema (BaseSchema):
    id: UUID
