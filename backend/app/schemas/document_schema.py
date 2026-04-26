from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class DocumentChunk(BaseModel):
    index: int
    text_preview: str
    char_count: int


class RedFlag(BaseModel):
    category: str
    label: str
    severity: str
    evidence: str
    suggested_action: str


class DocumentAnalysis(BaseModel):
    id: Optional[int] = None
    document_id: Optional[str] = None
    filename: str
    status: str
    page_count: int
    saved_path: str
    text_preview: str
    chunks: List[DocumentChunk]
    summary: str
    extracted_fields: Dict[str, Any]
    extracted_sections: Dict[str, Optional[str]]
    red_flags: List[RedFlag]
    missing_fields: List[str]
    risk_level: str
    confidence: str
    valuation_draft: Dict[str, Any]
    notes: List[str]


class DocumentAnalysisRead(BaseModel):
    id: int
    filename: str
    saved_path: str
    page_count: int
    extracted_text_preview: str
    summary: str
    extracted_fields: Dict[str, Any]
    red_flags: List[Dict[str, Any]]
    missing_fields: List[str]
    confidence: str
    created_at: datetime
    updated_at: datetime
