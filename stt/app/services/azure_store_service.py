import json
import os
from datetime import datetime
from typing import List, Optional

from azure.identity import DefaultAzureCredential
from azure.storage.blob import ContentSettings
from azure.storage.blob.aio import BlobServiceClient
from loguru import logger

from app.constants import (
    CONTENT_TYPE_AUDIO,
    CONTENT_TYPE_TEXT,
    ENCODING_TEXT,
    METADATA_BLOB_PATH,
)
from app.models.session import User
from app.services.store_service import StoreService


class AzureStoreService(StoreService):
    """Azure storage account implementation of store service.

    If not used as a context manager, then the caller is responsible for calling close().

    Args:
        StoreService (StoreService): Abstract store service
    """

    def __init__(self, user_id: str, container_name: Optional[str] = None):
        super().__init__(user_id, container_name)

    async def __aenter__(self):
        # For unit testing purposes
        if isinstance(os.environ.get("AZURE_STORAGE_CONNECTION_STRING"), str):
            self.blob_service_client = BlobServiceClient.from_connection_string(
                os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
            )
        else:
            self.blob_service_client = BlobServiceClient(
                account_url=os.getenv("AZURE_ACCOUNT_URL"),
                credential=DefaultAzureCredential(),
            )
        self.container_client = self.blob_service_client.get_container_client(
            self.container_name
        )
        return self

    async def __aexit__(self, *args):
        await self.close()

    async def read_metadata(self, session_id: str) -> User:
        blob_path = self._generate_blob_path(
            self.user_id, session_id, METADATA_BLOB_PATH
        )
        user_data_json = await self._read_blob(blob_name=blob_path, binary=False)
        return User(**json.loads(user_data_json))

    async def get_file(
        self, session_id: str, file_name: str, binary: bool
    ) -> str | bytes:
        blob_path = self._generate_blob_path(
            user_id=self.user_id, session_id=session_id, sub_path=f"data/{file_name}"
        )
        return await self._read_blob(blob_path, binary)

    async def get_prompt(self, prompt_file: str) -> str:
        blob_path = self._generate_prompt_path(prompt_file)
        return await self._read_blob(blob_path, binary=False)

    async def save_output(self, session_id: str, output_type: str, content: str) -> str:
        blob_path = self._generate_blob_path(
            self.user_id, session_id, f"data/{output_type}.txt"
        )
        await self._write_blob(blob_path, content, content_type=CONTENT_TYPE_TEXT)
        return blob_path

    async def save_transcript(self, session_id: str, content: str) -> str:
        blob_path = self._generate_blob_path(
            self.user_id,
            session_id,
            f"data/transcript_{datetime.now().strftime('%Y%m%d')}.txt",
        )
        await self._write_blob(blob_path, content, content_type=CONTENT_TYPE_TEXT)
        return blob_path

    async def save_audio(
        self,
        session_id: str,
        name: str,
        audio_content: bytes,
    ) -> str:
        blob_path = self._generate_blob_path(self.user_id, session_id, f"data/{name}")
        content_type = CONTENT_TYPE_AUDIO

        await self._write_blob(
            blob_path, content=audio_content, content_type=content_type
        )
        return blob_path

    async def update_metadata(self, user: User) -> User:
        blob_path = self._generate_blob_path(
            user.id_, user.session.id_, METADATA_BLOB_PATH
        )
        content = user.model_dump_json()
        content_type = CONTENT_TYPE_TEXT

        await self._write_blob(
            blob_name=blob_path, content=content, content_type=content_type
        )
        return user

    async def _read_blob(self, blob_name: str, binary: bool) -> str | bytes:
        blob_client = self.blob_service_client.get_blob_client(
            container=self.container_name, blob=blob_name
        )
        try:
            encoding = None if binary else ENCODING_TEXT
            blob_content = await blob_client.download_blob(encoding=encoding)
            return await blob_content.readall()
        except Exception as e:
            logger.error(f"Error reading blob '{blob_name}': {str(e)}")
            raise

    async def _write_blob(self, blob_name: str, content: bytes, content_type: str):
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name, blob=blob_name
            )
            await blob_client.upload_blob(
                content,
                overwrite=True,
                content_settings=ContentSettings(content_type=content_type),
            )
            logger.info(
                "Content uploaded successfully to "
                + f"https://{self.blob_service_client.account_name}.blob.core.windows.net/"
                + f"{self.container_name}/{blob_name}"
            )

        except Exception as err:
            logger.error(f"Failed to upload content to blob '{blob_name}': {err}")
            raise

    def _generate_blob_path(self, user_id: str, session_id: str, sub_path: str):
        blob_path = f"{user_id}/{session_id}/{sub_path}"
        return blob_path

    def _generate_prompt_path(self, prompt_file: str):
        return f"prompts/{prompt_file}"

    async def list_blobs(self, prefix: str = None) -> List[str]:
        return [
            blob.name
            async for blob in self.container_client.list_blobs(name_starts_with=prefix)
        ]

    async def close(self):
        await self.blob_service_client.close()
