from app.schemas.base import BaseSchema

class Token(BaseSchema):
    access_token: str


class TokenData(BaseSchema):
    user_id: str | None = None
