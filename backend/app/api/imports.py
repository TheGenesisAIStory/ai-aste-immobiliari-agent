from __future__ import annotations

import uuid
from fastapi import APIRouter, File, UploadFile, HTTPException

from app.schemas.import_schema import (
    UrlImportRequest,
    UrlImportResponse,
    PdfImportResponse,
    ParseRequest,
    ValuateDraftRequest,
)
from app.services.import_service import import_from_url, import_from_pdf
from app.services.parser_service import parse_auction_text

router = APIRouter(prefix="/imports", tags=["imports"])


@router.post("/url", response_model=UrlImportResponse)
def import_url(payload: UrlImportRequest):
    try:
        import_id, path, text = import_from_url(str(payload.source_url))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "import_id": import_id,
        "source_url": str(payload.source_url),
        "status": "ok",
        "extracted_text_preview": text[:500],
        "saved_path": path,
    }


@router.post("/pdf", response_model=PdfImportResponse)
async def import_pdf(file: UploadFile = File(...)):
    try:
        content = await file.read()
        import_id, path, text, pages = import_from_pdf(file.filename, content)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "import_id": import_id,
        "filename": file.filename,
        "status": "ok",
        "page_count": pages,
        "extracted_text_preview": text[:500],
        "saved_path": path,
    }


@router.post("/parse")
def parse(payload: ParseRequest):
    return parse_auction_text(payload.text, payload.source_url)


@router.post("/valuate-draft")
def valuate_draft(payload: ValuateDraftRequest):
    parsed = payload.parsed_fields or parse_auction_text(payload.text or "", payload.source_url)[
        "parsed_fields"
    ]

    missing_required = [
        "estimated_market_price_per_sqm",
        "renovation_cost",
        "other_costs",
        "expected_monthly_rent",
    ]

    return {
        "draft": parsed,
        "missing_required_fields": missing_required,
    }
