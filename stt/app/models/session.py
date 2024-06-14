from typing import Dict, Optional
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field
from uuid import uuid4


class Task(BaseModel):
    input_file: Optional[str] = None
    output_file: str


class AudioData(BaseModel):
    name: str
    duration: float
    size: int
    type: str
    file: Optional[str] = None


class SessionStatus(Enum):
    NOTHING = 0
    PROCESSING = 1
    DONE = 2


def generate_id():
    return str(uuid4())


class Session(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id_: str = Field(default_factory=generate_id)
    audio: AudioData
    current_task: int = 1
    transcript_version: Optional[str] = None
    tasks: Dict[str, Task] = Field(default_factory=dict)

    status: SessionStatus = SessionStatus.NOTHING

    transcript_file: Optional[str] = None
    transcript_content: Optional[str] = None
    # TODO: might make sense to add two more fields: initial_report and corrected_report instead of corrected file below
    transcript_corrected_file: Optional[str] = None

    output_file: Optional[str] = None

    def set_transcript_version(self) -> None:
        self.transcript_version = self.get_task_key()

    def increment_task(self) -> None:
        self.current_task += 1

    def get_task_key(self):
        return f"t{self.current_task}"

    def add_task(self, input_file: str, output_file: str) -> None:
        task_key = self.get_task_key()
        self.tasks[task_key] = Task(input_file=input_file, output_file=output_file)

    def fetch_task(self, task_nr: int) -> Task:
        task_key = f"t{task_nr}"
        return self.tasks[task_key]


class User(BaseModel):
    id_: str
    session: Session
