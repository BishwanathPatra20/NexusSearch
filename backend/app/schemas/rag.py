from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class RagSourceOut(BaseModel):
    chunk_id: int
    document_id: int
    document_title: str
    file_name: str
    page_number: Optional[int] = None
    snippet: str
    score: float = 0.0


class RagChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    history: List[Dict[str, str]] = Field(default_factory=list)


class RagChatResponse(BaseModel):
    answer: str
    mode: Literal["ollama", "extractive"]
    sources: List[RagSourceOut] = Field(default_factory=list)
    ollama_available: bool = False
    model: Optional[str] = None
    disclaimer: str = (
        "Exploratory local RAG — not reviewed official knowledge. "
        "Use Governed Ask for approved answers."
    )


class RagStatusOut(BaseModel):
    enabled: bool
    llm_enabled: bool
    ollama_base_url: str
    ollama_model: str
    ollama_reachable: bool
    ollama_error: Optional[str] = None
