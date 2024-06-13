from app.models.session import User
from app.services.store_service import StoreService
from app.services.azure_store_service import AzureStoreService
from app.services.openai_service import OpenAIService
from app.utils.audio_tools import compress_audio_file
from loguru import logger


class TranscribeService:
    def __init__(self, 
                 store_service: StoreService,
                 openai_service: OpenAIService):
        self.store_service = store_service
        self.openai_service = OpenAIService()

    async def transcribe_audio(self, session_id) -> User:
        async with self.store_service as store_service:
            user = await store_service.read_metadata(session_id)
            logger.info(f"Reading audio file: container={store_service.container_name}, file={user.session.audio.name}")
            audio_data = compress_audio_file(
                await store_service.get_file(session_id, user.session.audio.name, binary=True)
            )

            transcript = await self.openai_service.transcribe(
                audio_data=audio_data, 
                audio_name=user.session.audio.name
            )

            user.session.transcript_file = await store_service.save_transcript(
                user.session.id_, transcript
            )

            return await store_service.update_metadata(user)
