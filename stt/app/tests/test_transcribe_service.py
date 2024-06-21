from pytest_mock import MockerFixture

from app.services.openai_service import OpenAIService
from app.services.store_service import StoreService
from app.services.transcribe_service import TranscribeService
from app.tests.factories import UserFactory


class TestTranscribeService:
    async def test_transcribe_audio(
        self,
        transcribe_service: TranscribeService,
        azure_store_service: StoreService,
        openai_service: OpenAIService,
        mocker: MockerFixture,
    ):
        # Arrange
        user = UserFactory()
        session_id = user.session.id_
        audio_data = b"audio_data"
        transcript = b"transcript"

        mocker.patch.object(azure_store_service, "read_metadata", return_value=user)
        mocker.patch.object(azure_store_service, "get_file", return_value=audio_data)
        mocked_save_transcript = mocker.patch.object(
            azure_store_service, "save_transcript"
        )
        mocked_update_metadata = mocker.patch.object(
            azure_store_service, "update_metadata", return_value=user
        )

        mocker.patch(
            "app.utils.audio_tools.compress_audio_file",
            return_value=audio_data,
        )

        mocker.patch.object(openai_service, "transcribe", return_value=transcript)

        # Act
        actual = await transcribe_service.transcribe_audio(session_id)

        # Assert
        assert actual == user
        mocked_save_transcript.assert_called_once_with(user.session.id_, transcript)
        mocked_update_metadata.assert_called_once_with(user)
