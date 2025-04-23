from functools import cached_property
from typing import Literal, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

class AuthSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AUTH_")

    SECRET_KEY: str = "JL9s6YkzQp2WYV7uuWgu9EpV2HxpWU4xPYtcq2KCpqCdUaky97JFBszb5YKaQUMA"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 12

class GitSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="GIT_")

    HASH: Optional[str] = None
    BRANCH: Optional[str] = None
    TAG: Optional[str] = None
    PIPELINE_NUMBER: Optional[str] = None

class AWSSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AWS_")
    REGION_NAME: str = "us-east-1"


class S3Settings(AWSSettings):
    S3_BUCKET: str = "highkick-heap"


class AgentConfig(BaseSettings):
    CONFIG_PATH: str = "./"


class BedrockClientSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="BEDROCK_")

    REGION_NAME: str = "us-east-1"

    KNOWLEDGE_BASE_ID: str = "CE6Z3XBFD4"
    DATA_SOURCE_ID: str = "0UKMQMTJKU"
    MODEL_ARN: str = "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0"
    MODEL_ID: str = "anthropic.claude-3-5-sonnet-20240620-v1:0"

    RETRIEVAL_RESULTS: int = 10

    JUDGE_MODEL_ID: str = "anthropic.claude-v2:1"
    ADMIN_MODEL_ARN: str = "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0"
    ADMIN_RETRIEVAL_RESULTS: int = 10


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="./.env", env_file_encoding="utf-8"
    )

    ENVIRONMENT_NAME: Literal["local", "dev", "main"] = "local"

    SERVICE_NAME: str = "HIGHKICK DASHBOARD"
    SERVICE_VERSION: str = "0.1.0"
    SERVICE_HOST: str = "0.0.0.0"
    SERVICE_PORT: int = 9900

    NUMBER_OF_WORKERS: int = 1
    DEBUG: bool = False
    TESTING: bool = False
    RELOAD: bool = False

    auth: AuthSettings = AuthSettings()
    git: GitSettings = GitSettings()
    aws: AWSSettings = AWSSettings()
    bedrock: BedrockClientSettings = BedrockClientSettings()
    s3: S3Settings = S3Settings()
    agent_config: AgentConfig = AgentConfig()


settings = Settings()
