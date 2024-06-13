from pytest_mock import MockerFixture

from app.services.chat_service import ChatService
from app.services.store_service import StoreService
from app.services.prompt_service import PromptService
from app.services.openai_service import OpenAIService
from app.tests.factories import UserFactory


class TestChatService:
    async def test_get_transcript_output(
        self,
        azure_store_service: StoreService,
        prompt_service: PromptService,
        chat_service: ChatService,
        mocker: MockerFixture,
    ):
        # Arrange
        user = UserFactory()
        transcript = "transcript"
        session_id = user.session.id_
        output_type = "output_type"
        output = "output"

        mocker.patch.object(azure_store_service, "read_metadata", return_value=user)
        mocker.patch.object(azure_store_service, "get_file", return_value=transcript)
        mocker.patch.object(azure_store_service, "update_metadata", return_value=user)
        mocked_save_output = mocker.patch.object(azure_store_service, "save_output")

        mocker.patch.object(
            prompt_service, "get_system_prompt", return_value="system prompt"
        )
        mocker.patch.object(
            prompt_service, "get_human_prompts", return_value="human prompt"
        )

        mocker.patch.object(OpenAIService, "apply_transform", return_value=output)

        # Act
        actual = await chat_service.get_transcript_output(session_id, output_type)

        # Assert
        assert actual == user
        mocked_save_output.assert_called_once_with(
            user.session.id_, output_type, output
        )
