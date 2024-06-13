import os
from typing import List, Dict, Union

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AzureOpenAI
from aiohttp import ClientSession, FormData
from loguru import logger


class OpenAIService:
    def __init__(self):
        self.llm = self._get_llm()
     
    def _get_llm(self) -> AzureChatOpenAI:
        # """
        # Get Large Language Model object connecting to GPTs in Azure
        # """
        #endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
        endpoint = "https://htm-oaisdc-dev.openai.azure.com/"
        logger.info(f"Endpoint={endpoint}")
        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
        )

        llm = AzureOpenAI(
            azure_endpoint=endpoint,
            azure_ad_token_provider=token_provider,
            api_version="2024-02-01",
        )
        logger.info(f"LLM={llm}")
        return llm

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

    @staticmethod
    async def apply_transform(
        system_prompt: str, human_prompt: str, language: str, transcript: str
    ) -> str | List[str | Dict]:
        prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", human_prompt),
            ]
        )
        chain = prompt_template | self._get_llm()
        answer_object = await chain.ainvoke(
            {
                "language": language,
                "transcript": transcript,
            }
        )
        return answer_object.content

    @staticmethod
    async def transcribe(
        audio_data: bytes,
        audio_name: str,
        language: str = "nl",
    ) -> bytes:

        # Initialise `aiohttp.ClientSession` for asynchronous AzureOpenAI Whisper transcribe
        async with ClientSession() as session:
            url, headers = OpenAIService._get_url_and_headers()
            logger.info(f"URL={url}, headers={headers}")
            # Prepare the audio file in FormData
            data = FormData()
            data.add_field(
                "file", audio_data, filename=audio_name, content_type="audio/wav"
            )

            # Set the language parameter if necessary
            params = {"language": language}

            try:
                async with session.post(
                    url, headers=headers, data=data, params=params
                ) as response:
                    response.raise_for_status()
                    transcript_data = await response.json()
                    transcript = transcript_data["text"].encode("utf-8")
                    return transcript

            except Exception as err:
                logger.error("Call to Azure OpenAI failed", err)

    
