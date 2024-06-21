import json
import os

from app.constants import HUMAN_PROMPTS_BLOB_NAME, SYSTEM_PROMPT_BLOB_NAME
from app.services.store_service import StoreService


class PromptService:
    user_id: str

    def __init__(self, user_id: str, store_service: StoreService) -> None:
        self.user_id = user_id
        self.store_service = store_service

    async def get_human_prompts(self, prompt_type: str) -> str:
        human_prompts = json.loads(
            await self.store_service.get_prompt(HUMAN_PROMPTS_BLOB_NAME)
        )
        return human_prompts[prompt_type]

    async def get_system_prompt(self) -> str:
        return await self.store_service.get_prompt(SYSTEM_PROMPT_BLOB_NAME)

    def load_system_content(self, path: str, prompt_type: str) -> str:
        return self._read_prompt(path, prompt_type, SYSTEM_PROMPT_BLOB_NAME)

    def load_user_content(self, path: str, prompt_type: str) -> str:
        return self._read_prompt(path, prompt_type, self._generate_user_content_uri())

    def _read_prompt(path: str, prompt_type: str, file_name: str):
        with open(os.path.join(path, prompt_type, file_name), "r") as f:
            return f.read()

    def _generate_user_content_uri(self) -> str:
        return f"meldingen/{self.user_id}.txt"
