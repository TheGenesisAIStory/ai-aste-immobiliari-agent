from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl


class UrlImportRequest(BaseModel):
    source_url: HttpUrl
    notes: Optional[str] = Field(default=None, max_length=1000)


class ParseRequest(BaseModel):
    text: str = Field(min_length=1)
    source_url: Optional[str] = None


class ValuateDraftRequest(BaseModel):
    text: Optional[str] = None
    parsed_fields: Optional[Dict[str, Any]] = None
    source_url: Optional[str] = None


class ImportResponse(BaseModel):
    id: Optional[int] = None
    import_id: str
    status: str
    extracted_text_preview: str
    saved_path: str
    parsed_fields: Dict[str, Any] = Field(default_factory=dict)
    missing_fields: List[str] = Field(default_factory=list)
    risk_keywords: List[str] = Field(default_factory=list)
    confidence: str = "bassa"


class UrlImportResponse(ImportResponse):
    source_url: str


class PdfImportResponse(ImportResponse):
    filename: str
    page_count: int


class ImportRecordRead(BaseModel):
    id: int
    source_type: str
    source_url: Optional[str]
    filename: Optional[str]
    saved_path: Optional[str]
    extracted_text_preview: str
    parsed_fields: Dict[str, Any]
    risk_keywords: List[str]
    missing_fields: List[str]
    confidence: str
    status: str
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime
