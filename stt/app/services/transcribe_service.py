from loguru import logger

from app.models.session import User
from app.services.openai_service import OpenAIService
from app.services.store_service import StoreService
from app.utils.audio_tools import compress_audio_file


class TranscribeService:
    def __init__(self, store_service: StoreService, openai_service: OpenAIService):
        self.store_service = store_service
        self.openai_service = openai_service

    async def transcribe_audio(self, session_id: str) -> User:
        user = await self.store_service.read_metadata(session_id)
        logger.info(
            f"Reading audio file: container={self.store_service.container_name}, file={user.session.audio.name}"
        )
        audio_data = compress_audio_file(
            await self.store_service.get_file(
                session_id, user.session.audio.name, binary=True
            )
        )

        transcript = await self.openai_service.transcribe(
            audio_data=audio_data, audio_name=user.session.audio.name
        )

        user.session.transcript_content = transcript
        user.session.transcript_file = await self.store_service.save_transcript(
            user.session.id_, transcript
        )

        return await self.store_service.update_metadata(user)

    async def get_transcript(self, session_id: str) -> User:
        user = await self.store_service.read_metadata(session_id)
        logger.info(f"file={user.session.transcript_file}")
        return user
