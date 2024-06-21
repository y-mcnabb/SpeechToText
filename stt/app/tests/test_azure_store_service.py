import random
from typing import Callable

from azure.storage.blob import ContainerClient
from faker import Faker

from app.constants import METADATA_BLOB_PATH
from app.services.azure_store_service import AzureStoreService
from app.tests.factories import UserFactory


class TestAzureStoreService:
    async def test_get_file(
        self,
        faker: Faker,
        upload_blob: Callable,
        azure_store_service: AzureStoreService,
    ):
        # Arrange
        session_id = faker.random_number()
        blob_name = " ".join(faker.random_letters())
        content = " ".join(faker.random_letters())
        path = f"{azure_store_service.user_id}/{session_id}/data/{blob_name}"
        upload_blob(path, bytes(content, "utf-8"))

        # Act
        result = await azure_store_service.get_file(session_id, blob_name, binary=False)

        # Assert
        assert result == content

    async def test_get_file_binary(
        self,
        faker: Faker,
        upload_blob: Callable,
        azure_store_service: AzureStoreService,
    ):
        # Arrange
        session_id = faker.random_number()
        blob_name = " ".join(faker.random_letters())
        content = " ".join(faker.random_letters())
        path = f"{azure_store_service.user_id}/{session_id}/data/{blob_name}"
        upload_blob(path, bytes(content, "utf-8"))

        # Act
        result = await azure_store_service.get_file(session_id, blob_name, binary=True)

        # Assert
        assert result == bytes(content, "utf-8")

    async def test_write_blob(
        self,
        faker: Faker,
        container_client: ContainerClient,
        azure_store_service: AzureStoreService,
    ):
        # Arrange
        blob_name = " ".join(faker.random_letters())
        content = " ".join(faker.random_letters())
        count_before = len(list(container_client.list_blob_names()))

        # Act
        await azure_store_service._write_blob(
            blob_name, bytes(content, "utf-8"), content_type="bytes"
        )

        # Assert
        blobs = list(container_client.list_blob_names())
        assert count_before < len(blobs)
        assert len(blobs) == 1
        assert blobs[0] == blob_name

    async def test_save_audio_file(
        self,
        faker: Faker,
        container_client: ContainerClient,
        azure_store_service: AzureStoreService,
    ):
        # Arrange
        blob_name = " ".join(faker.random_letters())
        session_id = faker.random_number()

        # Create random audio
        audio_data = bytes(random.randint(0, 255) for _ in range(20))
        audio_bytearray = bytearray(audio_data)
        audio_bytearray[0] = 0

        count_before = len(list(container_client.list_blob_names()))
        expected_path = f"{azure_store_service.user_id}/{session_id}/data/{blob_name}"

        # Act
        await azure_store_service.save_audio(
            session_id=session_id,
            name=blob_name,
            audio_content=bytes(audio_bytearray),
        )

        # Assert
        blobs = list(container_client.list_blob_names())
        assert count_before < len(blobs)
        assert len(blobs) == 1
        assert blobs[0] == expected_path

    async def test_read_metadata(
        self,
        upload_blob: Callable,
        azure_store_service: AzureStoreService,
    ):
        # Arrange
        user = UserFactory()
        content = user.model_dump_json()
        path = f"{user.id_}/{user.session.id_}/{METADATA_BLOB_PATH}"

        upload_blob(path, bytes(content, "utf-8"))

        azure_store_service.user_id = user.id_

        # Act
        result = await azure_store_service.read_metadata(user.session.id_)

        # Assert
        assert result == user

    async def test_update_metadata(
        self,
        container_client: ContainerClient,
        upload_blob: Callable,
        azure_store_service: AzureStoreService,
    ):
        # Arrange
        old_user = UserFactory()
        user = UserFactory()

        old_user.id_ = user.id_
        old_user.session.id_ = user.session.id_
        old_metadata = user.model_dump_json()

        azure_store_service.user_id = user.id_

        path = f"{old_user.id_}/{old_user.session.id_}/{METADATA_BLOB_PATH}"
        upload_blob(path, bytes(old_metadata, "utf-8"))
        count_before = len(list(container_client.list_blob_names()))

        # Act
        result = await azure_store_service.update_metadata(user)

        # Assert
        blobs = list(container_client.list_blob_names())
        assert result == user
        assert result != old_user
        assert count_before == len(blobs)
        assert len(blobs) == 1
        assert blobs[0] == path
