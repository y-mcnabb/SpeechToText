import os
from typing import Any, AsyncGenerator, Callable

import pytest
from azure.storage.blob import BlobServiceClient, ContainerClient
from faker import Faker

from app.services.azure_store_service import AzureStoreService
from app.services.chat_service import ChatService
from app.services.openai_service import OpenAIService
from app.services.prompt_service import PromptService
from app.services.stt_service import SttService
from app.services.transcribe_service import TranscribeService


def pytest_generate_tests():
    """This function is run once at the very start of a test run."""
    # Set Azurite dev credentials
    os.environ["AZURE_STORAGE_CONNECTION_STRING"] = (
        "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"
    )
    os.environ["STORAGE_CONTAINER"] = "test-container"


@pytest.fixture
def blob_service_client() -> BlobServiceClient:
    return BlobServiceClient.from_connection_string(
        os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
    )


@pytest.fixture
def create_container(blob_service_client: BlobServiceClient):
    blob_service_client.create_container(os.environ.get("STORAGE_CONTAINER"))
    yield
    blob_service_client.delete_container(os.environ.get("STORAGE_CONTAINER"))


@pytest.fixture
def container_client(
    create_container, blob_service_client: BlobServiceClient
) -> ContainerClient:
    return blob_service_client.get_container_client(os.environ.get("STORAGE_CONTAINER"))


@pytest.fixture
def upload_blob(container_client: ContainerClient) -> Callable:
    created_blobs = []

    def _upload_blob(name: str, content: bytes):
        container_client.upload_blob(name, content)
        created_blobs.append(name)

    return _upload_blob


@pytest.fixture
async def azure_store_service(
    faker: Faker,
) -> AsyncGenerator[Any, AzureStoreService]:
    async with AzureStoreService(
        user_id=faker.random_number(),
        container_name=os.environ.get("STORAGE_CONTAINER"),
    ) as service:
        yield service


@pytest.fixture
def openai_service():
    return OpenAIService()


@pytest.fixture
def chat_service(
    azure_store_service: AzureStoreService,
    prompt_service: PromptService,
    openai_service: OpenAIService,
) -> ChatService:
    return ChatService(
        store_service=azure_store_service,
        prompt_service=prompt_service,
        openai_service=openai_service,
    )


@pytest.fixture
def transcribe_service(
    azure_store_service,
    openai_service: OpenAIService,
) -> TranscribeService:
    return TranscribeService(
        store_service=azure_store_service, openai_service=openai_service
    )


@pytest.fixture
def prompt_service(
    faker: Faker, azure_store_service: AzureStoreService
) -> PromptService:
    return PromptService(
        user_id=faker.random_number(), store_service=azure_store_service
    )


@pytest.fixture
def stt_service(
    transcribe_service: TranscribeService,
    chat_service: ChatService,
    store_service: AzureStoreService,
) -> SttService:
    return SttService(
        transcribe_service=transcribe_service,
        chat_service=chat_service,
        store_service=store_service,
    )
