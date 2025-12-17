from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class InputType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    PDF = "pdf"
    AUDIO = "audio"
    YOUTUBE = "youtube"


class TaskType(str, Enum):
    SUMMARIZE = "summarize"
    SENTIMENT = "sentiment"
    CODE_EXPLAIN = "code_explain"
    CHAT = "chat"


class IntentStatus(str, Enum):
    CLEAR = "clear"
    AMBIGUOUS = "ambiguous"
    GENERAL_CHAT = "chat"


class ChatResponse(BaseModel):
    response: str
    session_id: str
    requires_clarification: bool = False
    task_performed: Optional[str] = None


class IntentAnalysis(BaseModel):
    status: IntentStatus
    detected_task: Optional[TaskType] = None
    confidence: float = Field(ge=0.0, le=1.0)
    clarifying_question: Optional[str] = None
    reasoning: Optional[str] = None


class SummarizationResult(BaseModel):
    one_line: str
    bullets: list[str]
    five_sentence: str


class SentimentResult(BaseModel):
    label: str
    confidence: float
    justification: str


class CodeExplanationResult(BaseModel):
    explanation: str
    bugs: list[str] = []
    time_complexity: str
    space_complexity: Optional[str] = None


class ExtractionResult(BaseModel):
    input_type: InputType
    extracted_text: str
    metadata: dict = {}
    error: Optional[str] = None
