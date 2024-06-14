from app.models.session import User
from app.services.prompt_service import PromptService
from app.services.store_service import StoreService
from app.services.openai_service import OpenAIService


class ChatService:

    def __init__(self, store_service: StoreService, prompt_service: PromptService):
        self.store_service = store_service
        self.prompt_service = prompt_service

    async def apply_transform(
        self,
        store_service: StoreService,
        transcript: str,
        output_type: str,
        language: str = "nl",
    ) -> str:

        system_prompt = await self.prompt_service.get_system_prompt(store_service)
        human_prompt = await self.prompt_service.get_human_prompts(
            store_service, output_type
        )

        return await OpenAIService.apply_transform(
            system_prompt=system_prompt,
            human_prompt=human_prompt,
            language=language,
            transcript=transcript,
        )

    async def get_transcript_output(self, session_id: str, output_type: str) -> User:
        async with self.store_service as service:
            user = await service.read_metadata(session_id)
            transcript = await service.get_file(
                user.session.transcript_corrected_file, binary=False
            )

            system_prompt = await self.prompt_service.get_system_prompt(service)
            human_prompt = await self.prompt_service.get_human_prompts(
                service, output_type
            )

            output = await OpenAIService.apply_transform(
                system_prompt=system_prompt,
                human_prompt=human_prompt,
                language="Dutch",
                transcript=transcript,
            )

            user.session.output_file = await service.save_output(
                session_id, output_type, output
            )

            return await service.update_metadata(user)
