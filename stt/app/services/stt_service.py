from fastapi import HTTPException
from pydantic import ValidationError

from app.models.session import User
from app.services.chat_service import ChatService
from app.services.store_service import StoreService
from app.services.transcribe_service import TranscribeService


class SttService:
    def __init__(
        self,
        transcribe_service: TranscribeService,
        chat_service: ChatService,
        store_service: StoreService,
    ):
        self.store_service = store_service
        self.chat_service = chat_service
        self.transcribe_service = transcribe_service

    async def save_audio(self, user: User, audio_content: bytes) -> None:
        user_id = user.id_
        session_id = user.session.id_

        try:
            async with self.store_service as service:
                file_path = await service.save_audio(
                    user_id,
                    session_id,
                    user.session.audio.name,
                    "audio/wave",
                    audio_content,
                )
                user.session.audio.file = file_path
                await service.update_metadata(user)
                return user

        except ValidationError as err:
            raise HTTPException(status_code=422, detail=str(err))

        except Exception as err:
            raise HTTPException(status_code=500, detail=str(err))

    async def transcribe(self, user_id: str, session_id: str) -> User:
        return await self.transcribe_service.transcribe_audio(session_id)

    async def output(self, user_id: str, session_id: str, output_type: str) -> any:
        return await self.chat_service.get_transcript_output(
            user_id, session_id, output_type
        )
