import json
import os
from typing import Optional, List
from datetime import datetime

from azure.storage.blob import ContentSettings
from azure.storage.blob.aio import BlobServiceClient
from azure.identity import DefaultAzureCredential
from loguru import logger

from app.models.session import User
from app.services.store_service import StoreService


class AzureStoreService(StoreService):
    def __init__(self, user_id: str, container_name: Optional[str] = None):
        super().__init__(user_id, container_name)
    """
    Azure Store Service.

    If not used as a context manager, then the caller is responsible for calling close().
    """

    async def __aenter__(self):
        # For unit testing purposes
        if isinstance(os.environ.get("AZURE_STORAGE_CONNECTION_STRING"), str):
            self.blob_service_client = BlobServiceClient.from_connection_string(
                os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
            )
        else:
            self.blob_service_client = BlobServiceClient(
                account_url="https://htmtcadatadev.blob.core.windows.net/", #os.getenv("AZURE_ACCOUNT_URL"),
                credential=DefaultAzureCredential(),
            )
        self.container_client = self.blob_service_client.get_container_client(self.container_name)
        return self

    async def __aexit__(self, *args):
        await self.blob_service_client.close()

    async def read_metadata(self, session_id: str) -> User:
        blob_path = self._generate_blob_path(
            self.user_id, session_id, "meta/metadata.json"
        )
        user_data_json = await self._read_blob(
            blob_name=blob_path, binary=False
        )
        return User(**json.loads(user_data_json))


    async def get_file(self, session_id, file_name: str, binary: bool) -> str | bytes:
        blob_path = self._generate_blob_path(
            self.user_id, session_id, f"data/{file_name}"
        )
        return await self._read_blob(blob_path, binary)

    async def save_output(self, session_id: str, output_type: str, content: str) -> str:
        blob_path = self._generate_blob_path(
            self.user_id, session_id, f"data/{output_type}.txt"
        )
        await self._write_blob(blob_path, content, content_type="text/plain")
        return blob_path

    async def save_transcript(
            self, 
            session_id: str, 
            content: str
    ) -> str:
        blob_path = self._generate_blob_path(
            self.user_id,
            session_id,
            f"data/transcript_{datetime.now().strftime('%Y%m%d')}.txt",
        )
        await self._write_blob(blob_path, content, "text/plain")
        return blob_path

    async def save_audio(
        self,
        session_id: str,
        name: str,
        audio_content: bytes,
    ) -> str:
        blob_path = self._generate_blob_path(self.user_id, session_id, f"data/{name}")
        content_type = "audio/wav"

        await self._write_blob(
            blob_path, content=audio_content, content_type=content_type
        )

        return blob_path

    async def update_metadata(self, user: User) -> User:
        blob_path = self._generate_blob_path(
            user.id_, user.session.id_, "meta/metadata.json"
        )
        content = user.model_dump_json()
        content_type = "text/plain"

        await self._write_blob(
            blob_name=blob_path, content=content, content_type=content_type
        )

        return user

    async def _read_blob(self, blob_name: str, binary: bool) -> str | bytes:
        blob_client = self.blob_service_client.get_blob_client(
            container=self.container_name, blob=blob_name
        )
        try:
            blob_content = await blob_client.download_blob()

            if binary:
                blob = await blob_content.readall()
                # Download and return content as bytes for .wav or .json files
            else:
                blob = await blob_content.content_as_text()
            return blob
    
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
        return f"{user_id}/{session_id}/{sub_path}"

    async def list_blobs(self, prefix: str = None) -> List[str]:
        return [
            blob.name
            async for blob in self.container_client.list_blobs(name_starts_with=prefix)
        ]

    async def close(self):
        await self.blob_service_client.close()
