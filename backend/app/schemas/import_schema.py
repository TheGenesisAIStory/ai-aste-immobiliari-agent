from __future__ import annotations

from typing import Any, Dict, Optional

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
    import_id: str
    status: str
    extracted_text_preview: str
    saved_path: str


class UrlImportResponse(ImportResponse):
    source_url: str


class PdfImportResponse(ImportResponse):
    filename: str
    page_count: int
