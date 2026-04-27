from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


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


class FieldEvidence(BaseModel):
    value: Any = None
    confidence: str = "bassa"
    evidence: str = ""
    source: str = "rule_based"


class DocumentAnalysis(BaseModel):
    id: Optional[int] = None
    document_id: Optional[str] = None
    filename: str
    analysis_mode: str = "rule_based"
    status: str
    page_count: int
    saved_path: str
    text_preview: str
    chunks: List[DocumentChunk]
    summary: str
    fields: Dict[str, FieldEvidence] = Field(default_factory=dict)
    extracted_fields: Dict[str, Any]
    extracted_sections: Dict[str, Optional[str]]
    red_flags: List[RedFlag]
    missing_fields: List[str]
    risk_level: str
    confidence: str
    ocr_used: bool = False
    ocr_pages: List[int] = Field(default_factory=list)
    text_extraction_method: str = "native"
    warnings: List[str] = Field(default_factory=list)
    rag_available: bool = False
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
    analysis_mode: str = "rule_based"
    ocr_used: bool = False
    ocr_pages: List[int] = []
    text_extraction_method: str = "native"
    warnings: List[str] = []
    created_at: datetime
    updated_at: datetime
