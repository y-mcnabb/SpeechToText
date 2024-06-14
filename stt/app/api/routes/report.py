from fastapi import Depends, APIRouter

from app.api.dependencies import get_stt_service
from app.models.session import User
from app.services.store_service import StoreService
from app.services.stt_service import SttService

router = APIRouter()


@router.post("/{user_id}/{session_id}/{output_type}", response_model=User)
async def generate_output(
    user_id: str,
    session_id: str,
    output_type: str,
    service: SttService = Depends(get_stt_service),
):
    return await service.output(user_id, session_id, output_type)
    # pass


@router.get("/{user_id}/{session_id}/", response_model=str)
async def get_output(
    user_id: str,
    session_id: str,  # store_service: StoreService = Depends(get_store_service)
):
    user: User = await store_service.read_metadata(session_id)
    return await store_service.get_output(user.session.output_file)
