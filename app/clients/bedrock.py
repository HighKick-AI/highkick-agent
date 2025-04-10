import json
import logging
import time
from typing import Any, List

from botocore.exceptions import BotoCoreError, ClientError

from app.core.settings import BedrockClientSettings
from app.schemas.sync import IngestionJobResponse, IngestionStatus

log = logging.getLogger(__name__)


class BedrockSyncError(Exception):
    pass


class BedrockClient:
    def __init__(
        self,
        client_agent: Any,
        client_agent_runtime: Any,
        client_runtime: Any,
        bedrock_settings: BedrockClientSettings,
    ) -> None:
        self._client_agent = client_agent
        self._client_agent_runtime = client_agent_runtime
        self._client_runtime = client_runtime
        self._bedrock_settings = bedrock_settings


    def sync_knowledge_base(self) -> IngestionJobResponse:
        try:
            response = self._client_agent.start_ingestion_job(
                knowledgeBaseId=self._bedrock_settings.KNOWLEDGE_BASE_ID,
                dataSourceId=self._bedrock_settings.DATA_SOURCE_ID,
            )
            return IngestionJobResponse(**response)

        except Exception as exc:
            raise BedrockSyncError(f"error starting sync: {str(exc)}") from exc


    def ask_llm(self, input_text: str) -> str:

        body = json.dumps(
            {
                # "prompt": input_text,
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 100000,
                # "temperature": 0,
                "messages": [
                    {"role": "user", "content": input_text}
                ]
            }
        )

        response = self._client_runtime.invoke_model(
            modelId=self._bedrock_settings.MODEL_ID, 
            body=body,
        )

        raw_result = response.get("body").read().decode('utf-8')
        result = json.loads(raw_result)
        print(result)
        return result["content"][0]["text"]
    

    def format_retrieval_response(self, retrieval_response: dict, tag: str):
        text = ''
        results = retrieval_response.get('retrievalResults')
        for result in results:
            text += f"""<{tag}>
    {result['content']['text']}
</{tag}>
"""
        return text

    def retrieve_db_schemas(self, account_id: str, input: str, formatted: bool = False) -> Any:

        filter_account = {
            "equals": {
                "key": "account_id",
                "value": account_id
            }
        }

        retrieval_response = self._client_agent_runtime.retrieve(
            retrievalQuery={"text": input},
            knowledgeBaseId= self._bedrock_settings.KNOWLEDGE_BASE_ID,
            retrievalConfiguration={
                "vectorSearchConfiguration": {
                    "numberOfResults": self._bedrock_settings.RETRIEVAL_RESULTS,
                    "filter": filter_account,
                }
            }
        )

        # print(self.format_retrieval_response(retrieval_response))
    
        if formatted:
            return self.format_retrieval_response(retrieval_response, "schema")
        
        return retrieval_response
