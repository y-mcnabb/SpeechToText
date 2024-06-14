import os
import json
from typing import Optional

from app.services.azure_store_service import AzureStoreService
from app.constants import HUMAN_PROMPTS_BLOB_NAME, SYSTEM_PROMPT_BLOB_NAME


class PromptService:
    user_id: str
    storage_service: Optional[AzureStoreService]

    def __init__(self, user_id: str) -> None:
        self.user_id = user_id

    async def get_human_prompts(
        self, azure_store_service: AzureStoreService, prompt_type: str
    ) -> str:
        async with azure_store_service as storage_service:
            human_prompts = json.loads(
                await storage_service.get_file(HUMAN_PROMPTS_BLOB_NAME, binary=False)
            )
            return human_prompts[prompt_type]

    async def get_system_prompt(self, azure_store_service: AzureStoreService) -> str:
        async with azure_store_service as storage_service:
            return await storage_service.get_file(SYSTEM_PROMPT_BLOB_NAME, binary=False)

    def load_system_content(self, path: str, prompt_type: str) -> str:
        return self._read_prompt(path, prompt_type, SYSTEM_PROMPT_BLOB_NAME)

    def load_user_content(self, path: str, prompt_type: str) -> str:
        return self._read_prompt(path, prompt_type, self._generate_user_content_uri())

    def _read_prompt(path: str, prompt_type: str, file_name: str):
        with open(os.path.join(path, prompt_type, file_name), "r") as f:
            return f.read()

    def _generate_user_content_uri(self) -> str:
        return f"meldingen/{self.user_id}.txt"
