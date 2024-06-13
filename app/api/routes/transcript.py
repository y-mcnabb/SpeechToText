from typing import Annotated

from fastapi import Depends, APIRouter

from app.api.dependencies import get_stt_service, get_azure_store_service, get_transcribe_service
from app.models.session import User
from app.services.store_service import StoreService
from app.services.stt_service import SttService
from app.services.azure_store_service import AzureStoreService
from app.services.transcribe_service import TranscribeService
import os

router = APIRouter()


@router.post("/{user_id}/{session_id}", response_model=User)
async def transcribe(
    user_id: str,
    session_id: str,
    store_service: Annotated[StoreService, Depends(get_azure_store_service)],
    stt_service: SttService = Depends(get_stt_service),
    transcribe_service: TranscribeService = Depends(get_transcribe_service)
):
    user = await transcribe_service.transcribe_audio(session_id)
    return user


@router.get("/{user_id}/{session_id}", response_model=User)
async def get_transcript(
    user_id: str,
    session_id: str,
    #transcribe_service: TranscribeService = Depends(get_transcribe_service), 
    store_service: Annotated[AzureStoreService, Depends(get_azure_store_service)]
):
    user = await store_service.read_metadata(session_id)
    return await store_service.get_file(user.session.transcript_file)


@router.get("/allenv")
async def get_allenv():
    return os.environ.items()
