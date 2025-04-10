from app.schemas.base import BaseSchema

class DashboardRequestConsumeSchema (BaseSchema):
    text: str


class DashboardProduceSchema (BaseSchema):
    id: str
    name: str
    prompt: str
