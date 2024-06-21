import pytest
from pytest_mock import MockerFixture

from app.services.azure_store_service import AzureStoreService
from app.services.prompt_service import PromptService


class TestPromptService:
    async def test_get_human_prompts(
        self,
        azure_store_service: AzureStoreService,
        prompt_service: PromptService,
        mocker: MockerFixture,
    ):
        # Arrange
        json = '{"prompt1": "bar", "prompt2": "foo"}'
        mocker.patch.object(azure_store_service, "get_prompt", return_value=json)

        # Act
        result = await prompt_service.get_human_prompts("prompt1")

        # Assert
        assert result == "bar"

    async def test_get_human_prompts_key_not_found(
        self,
        azure_store_service: AzureStoreService,
        prompt_service: PromptService,
        mocker: MockerFixture,
    ):
        # Arrange
        json = '{"prompt1": "bar", "prompt2": "foo"}'
        mocker.patch.object(azure_store_service, "get_prompt", return_value=json)

        # Act
        # Assert
        with pytest.raises(KeyError):
            await prompt_service.get_human_prompts("prompt3")

    async def test_get_system_prompt(
        self,
        azure_store_service: AzureStoreService,
        prompt_service: PromptService,
        mocker: MockerFixture,
    ):
        # Arrange
        json = '{"prompt1": "bar", "prompt2": "foo"}'
        mocker.patch.object(azure_store_service, "get_prompt", return_value=json)

        # Act
        result = await prompt_service.get_system_prompt()

        # Assert
        assert result == json
