from fastapi import Depends

from app.services.azure_store_service import AzureStoreService
from app.services.chat_service import ChatService
from app.services.prompt_service import PromptService
from app.services.store_service import StoreService
from app.services.stt_service import SttService
from app.services.transcribe_service import TranscribeService
from app.services.openai_service import OpenAIService


async def get_azure_store_service(user_id: str):
    async with AzureStoreService(user_id) as service:
        yield service


def get_prompt_service(
        user_id: str, 
        store_service: StoreService = Depends(get_azure_store_service)
) -> PromptService:
    return PromptService(user_id=user_id, store_service=store_service)


def get_openai_service() -> OpenAIService:
    return OpenAIService()


def get_transcribe_service(
    store_service: StoreService = Depends(get_azure_store_service),
    openai_service: OpenAIService = Depends(get_openai_service),
) -> TranscribeService:
    return TranscribeService(store_service=store_service, openai_service=openai_service)


def get_chat_service(
    store_service: StoreService = Depends(get_azure_store_service),
    prompt_service: PromptService = Depends(get_prompt_service),
    openai_service: OpenAIService = Depends(get_openai_service),
) -> ChatService:
    return ChatService(store_service=store_service, 
                       prompt_service=prompt_service,
                       openai_service=openai_service)


def get_stt_service(
    store_service: StoreService = Depends(get_azure_store_service),
    transcribe_service: TranscribeService = Depends(get_transcribe_service),
    chat_service: ChatService = Depends(get_chat_service),
) -> SttService:
    return SttService(
        store_service=store_service,
        transcribe_service=transcribe_service,
        chat_service=chat_service,
    )



