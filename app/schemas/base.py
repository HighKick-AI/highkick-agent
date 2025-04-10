from uuid import UUID

from pydantic import BaseModel, ConfigDict

BaseConfig = ConfigDict(
    arbitrary_types_allowed=True,
    populate_by_name=True,
    from_attributes=True,
    alias_generator=None,
    json_encoders={
        UUID: lambda uuid: str(uuid),
    },
)


class BaseSchema(BaseModel):
    model_config = BaseConfig
