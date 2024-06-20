import os
from typing import List, Dict, Union

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AzureOpenAI
from aiohttp import ClientSession, FormData
from loguru import logger

import io


class OpenAIService:
    def _get_llm(self) -> AzureChatOpenAI:
        # """
        # Get Open AI client for whisper or LangChain Open AI client for GPT and chaining
        # """
        endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
        )

        openai_llm = AzureOpenAI(
            azure_endpoint=endpoint,
            azure_ad_token_provider=token_provider,
            api_version=os.environ["OPENAI_API_VERSION"],
        )

        langchain_llm = AzureChatOpenAI(
            model=os.environ["AZURE_GPT_DEPLOYMENT_NAME"],
            azure_endpoint=endpoint,
            azure_ad_token_provider=token_provider,
            api_version=os.environ["OPENAI_API_VERSION"],
        )

        return openai_llm, langchain_llm

    @staticmethod
    def _get_url_and_headers() -> Union[str, Dict[str, str]]:
        token_credential = DefaultAzureCredential()
        token = token_credential.get_token("https://management.azure.com/.default")
        url = (
            "https://management.azure.com/subscriptions/"
            + f"{os.getenv('AZURE_SUBSCRIPTION_ID')}/providers/Microsoft.CognitiveServices/locations/"
            + f"{os.getenv('REGION')}/models?api-version={os.getenv('OPENAI_API_VERSION')}"
        )
        headers = {"Authorization": "Bearer " + token.token}

        return (url, headers)

    #@staticmethod
    async def apply_transform(
        self,
        system_prompt: str, 
        human_prompt: str, 
        language: str, 
        transcript: str
    ) -> str | List[str | Dict]:
        prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", human_prompt),
            ]
        )
        _, llm = self._get_llm()
        chain = prompt_template | llm
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
        language: str = "nl",
    ) -> bytes:

        # Initialise `aiohttp.ClientSession` for asynchronous AzureOpenAI Whisper transcribe
        try:
            llm, _ = self._get_llm()
            audio_data_bytes = io.BytesIO(audio_data)
            audio_data_bytes.name = audio_name
            
            transcript_data = llm.audio.transcriptions.create(
                file = audio_data_bytes,
                model="whisper",
            )
            transcript = transcript_data.text
            logger.info(f"Transcript={transcript}")
            return transcript

        except Exception as err:
            logger.error("Call to Azure OpenAI failed", err)

    
