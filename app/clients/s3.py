from typing import Dict, List
import asyncio
import json
import logging
from typing import TYPE_CHECKING

from app.core.settings import S3Settings

if TYPE_CHECKING:
    from types_aiobotocore_s3.client import S3Client as S3ClientBoto


logger = logging.getLogger(__name__)


class S3Client:
    def __init__(
        self, s3_client: "S3ClientBoto", settings: S3Settings
    ) -> None:
        self._s3_client = s3_client
        self._bucket = settings.S3_BUCKET

    def get_db_schema_key(self, account_id: str, database_id: str) -> str :
        return f'schemas/{account_id}/{database_id}.md'
    
    def get_dashboard_html_key(self, account_id: str, dashboard_id: str) -> str :
        return f'dashboards/{account_id}/{dashboard_id}/index.html'
    
    def get_dashboard_data_key(self, account_id: str, dashboard_id: str) -> str :
        return f'dashboards/{account_id}/{dashboard_id}/data.json'
    
    def get_dashboard_script_key(self, account_id: str, dashboard_id: str) -> str :
        return f'dashboards/{account_id}/{dashboard_id}/script.py'

    async def put(self, key: str, data: str, content_type: str = None):
        try:
            if content_type is None:
                await self._s3_client.put_object(
                    Bucket=self._bucket,
                    Key=key,
                    Body=data,
                )
            else:
                await self._s3_client.put_object(
                    Bucket=self._bucket,
                    Key=key,
                    Body=data,
                    ContentType=content_type
                )
        except Exception as e:
            print(f'Failed to upload {key}: {e}')


    async def delete(self, key: str):
        try:
            await self._s3_client.delete_object(
                Bucket=self._bucket,
                Key=key,
            )
        except Exception as e:
            print(f'Failed to delete {key}: {e}')


    async def get_text(self, key: str) -> str:
        try:
            response = await self._s3_client.get_object(
                Bucket=self._bucket,
                Key=key
            )
            async with response['Body'] as stream:
                data = await stream.read()
            return data.decode("utf-8")
        except Exception as e:
            logger.error(f'Failed to retrieve {key}: {e}')

    async def put_db_schema_metadata(self, account_id: str, database_id: str): 
        
        attributes = {
            "account_id" : account_id
        }

        metadata = {
            "metadataAttributes" : attributes
        }

        key = self.get_db_schema_key(account_id=account_id, database_id=database_id)
        await self.put(key=f'{key}.metadata.json', data=json.dumps(metadata), content_type='application/json')

    async def put_db_schema(self, account_id: str, database_id: str, data: str, content_type: str): 
        key = self.get_db_schema_key(account_id=account_id, database_id=database_id)
        await self.put(key=key, data=data, content_type=content_type)
        await self.put_db_schema_metadata(account_id=account_id, database_id=database_id)

    async def get_db_schema(self, account_id: str, database_id: str): 
        key = self.get_db_schema_key(account_id=account_id, database_id=database_id)
        return await self.get_text(key=key)

    async def delete_db_schema(self, account_id: str, database_id: str): 
        key = self.get_db_schema_key(account_id=account_id, database_id=database_id)
        await self.delete(key=key)
        await self.delete(key=f'{key}.metadata.json')

    #############################
    ## Dashboard HTML

    async def put_dashboard_html(self, account_id: str, dashboard_id: str, data: str): 
        key = self.get_dashboard_html_key(account_id=account_id, dashboard_id=dashboard_id)
        await self.put(key=key, data=data, content_type="text/html")

    async def get_dashboard_html(self, account_id: str, dashboard_id: str): 
        key = self.get_dashboard_html_key(account_id=account_id, dashboard_id=dashboard_id)
        return await self.get_text(key=key)

    async def delete_dashboard_html(self, account_id: str, dashboard_id: str): 
        key = self.get_dashboard_html_key(account_id=account_id, dashboard_id=dashboard_id)
        await self.delete(key=key)

    #############################
    ## Dashboard data.json

    async def put_dashboard_data(self, account_id: str, dashboard_id: str, data: str): 
        key = self.get_dashboard_data_key(account_id=account_id, dashboard_id=dashboard_id)
        await self.put(key=key, data=data, content_type="application/json")

    async def get_dashboard_data(self, account_id: str, dashboard_id: str): 
        key = self.get_dashboard_data_key(account_id=account_id, dashboard_id=dashboard_id)
        return await self.get_text(key=key)

    async def delete_dashboard_data(self, account_id: str, dashboard_id: str): 
        key = self.get_dashboard_data_key(account_id=account_id, dashboard_id=dashboard_id)
        await self.delete(key=key)

    #############################
    ## Dashboard script.py

    async def put_dashboard_script(self, account_id: str, dashboard_id: str, data: str): 
        key = self.get_dashboard_script_key(account_id=account_id, dashboard_id=dashboard_id)
        await self.put(key=key, data=data, content_type="text/plain")

    async def get_dashboard_script(self, account_id: str, dashboard_id: str): 
        key = self.get_dashboard_script_key(account_id=account_id, dashboard_id=dashboard_id)
        return await self.get_text(key=key)

    async def delete_dashboard_script(self, account_id: str, dashboard_id: str): 
        key = self.get_dashboard_script_key(account_id=account_id, dashboard_id=dashboard_id)
        await self.delete(key=key)
