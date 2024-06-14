from app.services.azure_store_service import AzureStoreService
from azure.storage.blob import ContainerClient
from typing import Callable
import random
import pytest
from faker import Faker
from pytest_mock import MockerFixture
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
        async with azure_store_service as sut:
            result = await sut.get_file(session_id, blob_name, binary=False)

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
        async with azure_store_service as sut:
            result = await sut.get_file(session_id, blob_name, binary=True)

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
        async with azure_store_service as sut:
            await sut._write_blob(
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

        # Act
        async with azure_store_service as sut:
            await sut.save_audio(
                session_id=session_id,
                name=blob_name,
                audio_content=bytes(audio_bytearray),
            )

            expected_path = f"{sut.user_id}/{session_id}/data/{blob_name}"

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
        blob_name = "meta/metadata.json"

        content = user.model_dump_json()
        path = f"{user.id_}/{user.session.id_}/{blob_name}"

        upload_blob(path, bytes(content, "utf-8"))

        azure_store_service.user_id = user.id_

        # Act
        async with azure_store_service as sut:
            result = await sut.read_metadata(user.session.id_)

        # Assert
        result == user

    @pytest.mark.skip
    async def test_update_metadata(
        self,
        create_container,
        container_client: ContainerClient,
        azure_store_service: AzureStoreService,
        mocker: MockerFixture,
    ):

        # Arrange
        json = ""
        blob_name = "meta/metadata.json"
        session_id = "session_id"
        content = "bar"
        count_before = len(list(container_client.list_blob_names()))

        # Act
        async with azure_store_service as sut:
            await sut._write_blob(
                blob_name, bytes(content, "utf-8"), content_type="bytes"
            )

        expected_path = f"{sut.user_id}/{session_id}/data/{blob_name}"

        # Assert
        blobs = list(container_client.list_blob_names())
        assert count_before < len(blobs)
        assert len(blobs) == 1

        assert blobs[0] == expected_path


# async def update_metadata(self, user: User) -> User:
#     blob_path = self._generate_blob_path(
#         user.id_, user.session.id_, "meta/metadata.json"
#     )
#     content = user.model_dump_json()
#     content_type = "text/plain"
#     await self._write_blob(
#         blob_name=blob_path, content=content, content_type=content_type
#     )
#     return user

# async def read_metadata(self, session_id: str) -> User:
#     blob_path = self._generate_blob_path(
#         self.user_id, session_id, "meta/metadata.json"
#     )
#     user_data_json = await self.storage_service.read_blob(
#         blob_name=blob_path, binary=False
#     )
#     return User(**json.loads(user_data_json))
