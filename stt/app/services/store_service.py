import os
from typing import Optional
from abc import ABC, abstractmethod
from app.constants import STORAGE_CONTAINER

from app.models.session import User


class StoreService(ABC):
    """
    Abstract base store service
    """

    def __init__(self, user_id: str, container_name: Optional[str] = None) -> None:
        self.user_id = user_id
        self.container_name = STORAGE_CONTAINER

        if container_name:
            self.container_name = container_name

    @abstractmethod
    async def __aenter__(self):
        return self

    @abstractmethod
    async def __aexit__(self, *args):
        return self

    @abstractmethod
    async def get_file(self, file_name: str, binary: bool) -> str | bytes:
        raise NotImplementedError

    @abstractmethod
    async def save_audio(
        self,
        session_id: str,
        name: str,
        audio_content: bytes,
    ) -> str:
        raise NotImplementedError

    @abstractmethod
    async def read_metadata(self, session_id: str) -> User:
        raise NotImplementedError

    @abstractmethod
    async def update_metadata(self, user: User) -> User:
        raise NotImplementedError

    @abstractmethod
    async def save_output(self, session_id: str, output_type: str, content: str) -> str:
        raise NotImplementedError

    @abstractmethod
    async def save_transcript(self, session_id: str, content: str) -> str:
        raise NotImplementedError
