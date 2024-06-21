import io
import os
from typing import Dict, List, Union

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI
from loguru import logger
from openai import AzureOpenAI


class OpenAIService:
    @staticmethod
    def _get_open_ai_client() -> AzureOpenAI:
        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
        )

        return AzureOpenAI(
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            azure_ad_token_provider=token_provider,
            api_version=os.environ["OPENAI_API_VERSION"],
        )

    @staticmethod
    def _get_lang_chain_client() -> AzureChatOpenAI:
        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
        )

        return AzureChatOpenAI(
            model=os.environ["AZURE_GPT_DEPLOYMENT_NAME"],
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            azure_ad_token_provider=token_provider,
            api_version=os.environ["OPENAI_API_VERSION"],
        )

    async def apply_transform(
        self, system_prompt: str, human_prompt: str, language: str, transcript: str
    ) -> str | List[str | Dict]:
        prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", human_prompt),
            ]
        )
        client = OpenAIService._get_lang_chain_client()
        chain = prompt_template | client
        answer_object = await chain.ainvoke(
            {
                "language": language,
                "transcript": transcript,
            }
        )
        return answer_object.content

    async def transcribe(
        self,
        audio_data: bytes,
        audio_name: str,
    ) -> bytes:
        try:
            client = OpenAIService._get_open_ai_client()
            audio_data_bytes = io.BytesIO(audio_data)
            audio_data_bytes.name = audio_name

            transcript_data = client.audio.transcriptions.create(
                file=audio_data_bytes,
                model=os.getenv["AZURE_SPEECH_DEPLOYMENT_NAME"],
            )
            transcript = transcript_data.text
            logger.info(f"Transcript={transcript}")
            return transcript

        except Exception as err:
            logger.error("Call to Azure OpenAI failed", err)
