from __future__ import annotations

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
    chunks: list[DocumentChunk]
    extracted_sections: dict[str, str | None]
    red_flags: list[str]
    risk_level: str
    confidence: str
    notes: list[str]
