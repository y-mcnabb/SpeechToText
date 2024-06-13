from pytest_mock import MockerFixture

from app.services.transcribe_service import TranscribeService
from app.services.store_service import StoreService
from app.services.openai_service import OpenAIService
from app.tests.factories import UserFactory


class TestTranscribeService:
    async def test_transcribe_audio(
        self,
        transcribe_service: TranscribeService,
        azure_store_service: StoreService,
        mocker: MockerFixture,
    ):
        # Arrange
        user = UserFactory()
        session_id = user.session.id_
        audio_data = b"audio_data"
        transcript = b"transcript"

        mocker.patch.object(azure_store_service, "read_metadata", return_value=user)
        mocker.patch.object(azure_store_service, "update_metadata", return_value=user)
        mocker.patch.object(azure_store_service, "get_file", return_value=audio_data)
        mocked_save_transcript = mocker.patch.object(
            azure_store_service, "save_transcript"
        )

        mocker.patch(
            "app.utils.audio_tools.compress_audio_file",
            return_value=audio_data,
        )

        mocker.patch.object(OpenAIService, "transcribe", return_value=transcript)

        # Act
        actual = await transcribe_service.transcribe_audio(session_id)

        # Assert
        assert actual == user
        mocked_save_transcript.assert_called_once_with(user.session.id_, transcript)
