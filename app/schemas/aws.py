from typing import Literal, Optional, TypedDict

ServiceName = Literal["s3"]


class Credentials(TypedDict, total=False):
    service_name: str
    region_name: str
    endpoint_url: Optional[str]
