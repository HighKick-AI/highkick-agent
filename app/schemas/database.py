from uuid import UUID

from app.schemas.base import BaseSchema

class DatabaseConsumeSchema (BaseSchema):
    name: str
    tech: str

class DatabaseProduceSchema (BaseSchema):
    id: UUID
    name: str
    tech: str

class DatabaseSchemaConsumeSchema (BaseSchema):
    text: str

class DatabaseSchemaProduceSchema (BaseSchema):
    text: str
