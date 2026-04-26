from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel


class DocumentChunk(BaseModel):
    index: int
    text_preview: str
    char_count: int


class DocumentAnalysis(BaseModel):
    document_id: str
    filename: str
    status: str
    page_count: int
    saved_path: str
    text_preview: str
    chunks: List[DocumentChunk]
    extracted_sections: Dict[str, Optional[str]]
    red_flags: List[str]
    risk_level: str
    confidence: str
    notes: List[str]
