from app.models.session import User
from app.services.prompt_service import PromptService
from app.services.store_service import StoreService
from app.services.openai_service import OpenAIService
from loguru import logger

class ChatService:

    def __init__(self, 
                 store_service: StoreService, 
                 prompt_service: PromptService,
                 openai_service: OpenAIService):
        self.store_service = store_service
        self.prompt_service = prompt_service
        self.openai_service = openai_service

    async def get_transcript_output(self, session_id: str, output_type: str) -> User:
        user = await self.store_service.read_metadata(session_id)
        file_path = user.session.transcript_file
        file_name = file_path.split("/")[-1]
        transcript = await self.store_service.get_file(
            session_id=session_id, file_name=file_name, binary=False
            )

        system_prompt = await self.prompt_service.get_system_prompt()
        human_prompt = await self.prompt_service.get_human_prompts(output_type)

        output = await self.openai_service.apply_transform(
            system_prompt=system_prompt,
            human_prompt=human_prompt,
            language="Dutch",
            transcript=transcript,
            )

        user.session.output_content = output
        user.session.output_file = await self.store_service.save_output(
            user.session.id_, output_type, output
        )
        return await self.store_service.update_metadata(user)
