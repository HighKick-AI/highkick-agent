from app.schemas.base import BaseSchema

class AccessToken(BaseSchema):
    access_token: str

class ServiceToken(BaseSchema):
    service_token: str

