from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class DocumentQuestionRequest(BaseModel):
    question: str = Field(min_length=1)


class Citation(BaseModel):
    chunk_id: str
    page_number: Optional[int] = None
    text_snippet: str


class DocumentQuestionResponse(BaseModel):
    question: str
    answer: str
    confidence: str
    citations: List[Citation]
    mode: str


class DocumentChunkRead(BaseModel):
    document_id: int
    chunk_id: str
    page_number: Optional[int] = None
    text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
