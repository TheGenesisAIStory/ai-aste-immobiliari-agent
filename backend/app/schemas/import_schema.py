from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, HttpUrl


class UrlImportRequest(BaseModel):
    source_url: HttpUrl
    notes: str | None = Field(default=None, max_length=1000)


class ParseRequest(BaseModel):
    text: str = Field(min_length=1)
    source_url: str | None = None


class ValuateDraftRequest(BaseModel):
    text: str | None = None
    parsed_fields: dict[str, Any] | None = None
    source_url: str | None = None


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
