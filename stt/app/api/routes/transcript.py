import os

from fastapi import APIRouter, Depends

from app.api.dependencies import get_transcribe_service
from app.models.session import User
from app.services.transcribe_service import TranscribeService

router = APIRouter()


@router.post("/{user_id}/{session_id}", response_model=User)
async def transcribe(
    session_id: str,
    transcribe_service: TranscribeService = Depends(get_transcribe_service),
):
    user = await transcribe_service.transcribe_audio(session_id)
    return user


@router.get("/{user_id}/{session_id}", response_model=User)
async def get_transcript(
    user_id: str,
    session_id: str,
    transcribe_service: TranscribeService = Depends(get_transcribe_service),
):
    return await transcribe_service.get_transcript(session_id)
