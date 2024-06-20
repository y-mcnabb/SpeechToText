from typing import Annotated

from fastapi import APIRouter, File, UploadFile, Depends
from loguru import logger

from app.api.dependencies import get_azure_store_service
from app.models.session import Session, User, AudioData
from app.services.store_service import StoreService
from datetime import datetime

router = APIRouter()


# TODO: handle pushed audio the triggers the whole pipeline
# decouple upload audio from save audio due to privacy concerns
# talk to mendix FE about dependencies
@router.post("/{user_id}", response_model=User)
async def upload_audio(
    user_id: str,
    store_service: Annotated[StoreService, Depends(get_azure_store_service)],
    audio_file: UploadFile = File(...),
) -> User:
    session_name = audio_file.filename.split(".")[0]
    session = Session(
        audio=AudioData(
            name=f"{session_name}.wav",
            duration=10,
            size=audio_file.size,
            type=audio_file.content_type,
        )
    )
    user = User(id_=user_id, session=session)

    # TODO: content type guards
    try:
        logger.info(f"user_id: {user_id}")
        audio_in_bytes = await audio_file.read()
        await store_service.save_audio(
            session_id=session.id_,
            name=f"{session_name}.wav",
            audio_content=audio_in_bytes,
        )
        await store_service.update_metadata(user)
    except Exception as ex:
        logger.error("Upload Audio Failed ", ex)
        raise ex

    return user
