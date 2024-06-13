from __future__ import annotations

from azure.core.exceptions import ResourceNotFoundError
from azure.storage.blob import ContentSettings, PublicAccess
from azure.storage.blob.aio import BlobServiceClient, ContainerClient
from loguru import logger
from pydantic import BaseModel, Field
from app.constants import STORAGE_CONTAINER


class AzureFileProcessor(BaseModel):
    # connection_string: str = Field(..., env="AZURE_STORAGE_CONNECTION_STRING")
    container_name: str = STORAGE_CONTAINER
    blob_service_client: BlobServiceClient = None
    container_client: ContainerClient = None

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data) -> None:
        super().__init__(**data)
        connection_string = "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"
        self.blob_service_client = BlobServiceClient(
                account_url=os.getenv("AZURE_ACCOUNT_URL"),
                credential=DefaultAzureCredential(),
            )
        self.container_client = self._get_container_client()

    def _get_container_client(self) -> ContainerClient:
        """
        Ensure the container exists, or create it if it doesn't, and return the container client.
        """
        try:
            container_client = self.blob_service_client.get_container_client(
                self.container_name
            )

            # Attempt to retrieve container properties to check existence
            container_client.get_container_properties()
            logger.info(f"Container '{self.container_name}' already exists.")

        except ResourceNotFoundError:
            # Container does not exist, create it
            container_client = self.blob_service_client.create_container(
                self.container_name, public_access=PublicAccess.Container
            )
            logger.info(f"Container '{self.container_name}' has been created.")

        return container_client

    async def read_blob(self, blob_name: str, binary: bool) -> str | bytes:
        blob_client = self.container_client.get_blob_client(blob_name)
        blob_content = await blob_client.download_blob()

        if binary:
            blob_bytes = await blob_content.readall()
            return blob_bytes

        # Download and return content as bytes for .wav or .json files
        else:
            blob_text = await blob_content.content_as_text()
            return blob_text

    async def write_blob(
        self, blob_name: str, content: bytes, content_type: str
    ) -> None:
        try:
            blob_client = self.container_client.get_blob_client(blob=blob_name)
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

    async def close(self) -> None:
        await self.blob_service_client.close()
