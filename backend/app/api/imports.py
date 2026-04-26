from __future__ import annotations

import json
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories import import_repository
from app.schemas.import_schema import (
    ImportRecordRead,
    ParseRequest,
    PdfImportResponse,
    UrlImportRequest,
    UrlImportResponse,
    ValuateDraftRequest,
)
from app.services.import_service import import_from_pdf, import_from_url
from app.services.parser_service import parse_auction_text

router = APIRouter(prefix="/imports", tags=["imports"])


def _to_read(record) -> ImportRecordRead:
    return ImportRecordRead(
        id=record.id,
        source_type=record.source_type,
        source_url=record.source_url,
        filename=record.filename,
        saved_path=record.saved_path,
        extracted_text_preview=record.extracted_text_preview,
        parsed_fields=json.loads(record.parsed_fields_json or "{}"),
        risk_keywords=json.loads(record.risk_keywords_json or "[]"),
        missing_fields=json.loads(record.missing_fields_json or "[]"),
        confidence=record.confidence,
        status=record.status,
        error_message=record.error_message,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


@router.post("/url", response_model=UrlImportResponse)
def import_url(payload: UrlImportRequest, db: Session = Depends(get_db)):
    try:
        import_id, path, text = import_from_url(str(payload.source_url))
        parsed = parse_auction_text(text, str(payload.source_url))
        record = import_repository.create_import_record(
            db=db,
            source_type="url",
            source_url=str(payload.source_url),
            saved_path=path,
            text_preview=text[:500],
            parsed=parsed,
        )
    except Exception as exc:
        import_repository.create_import_record(
            db=db,
            source_type="url",
            source_url=str(payload.source_url),
            status="error",
            error_message=str(exc),
        )
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "id": record.id,
        "import_id": import_id,
        "source_url": str(payload.source_url),
        "status": "ok",
        "extracted_text_preview": text[:500],
        "saved_path": path,
        "parsed_fields": parsed["parsed_fields"],
        "missing_fields": parsed["missing_fields"],
        "risk_keywords": parsed["risk_keywords"],
        "confidence": parsed["confidence"],
    }


@router.post("/pdf", response_model=PdfImportResponse)
async def import_pdf(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        content = await file.read()
        import_id, path, text, pages = import_from_pdf(file.filename, content)
        parsed = parse_auction_text(text)
        record = import_repository.create_import_record(
            db=db,
            source_type="pdf",
            filename=file.filename,
            saved_path=path,
            text_preview=text[:500],
            parsed=parsed,
        )
    except Exception as exc:
        import_repository.create_import_record(
            db=db,
            source_type="pdf",
            filename=file.filename,
            status="error",
            error_message=str(exc),
        )
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "id": record.id,
        "import_id": import_id,
        "filename": file.filename,
        "status": "ok",
        "page_count": pages,
        "extracted_text_preview": text[:500],
        "saved_path": path,
        "parsed_fields": parsed["parsed_fields"],
        "missing_fields": parsed["missing_fields"],
        "risk_keywords": parsed["risk_keywords"],
        "confidence": parsed["confidence"],
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


@router.get("", response_model=List[ImportRecordRead])
def list_imports(db: Session = Depends(get_db)):
    return [_to_read(record) for record in import_repository.list_imports(db)]


@router.get("/{import_id}", response_model=ImportRecordRead)
def get_import(import_id: int, db: Session = Depends(get_db)):
    record = import_repository.get_import(db, import_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Import non trovato")
    return _to_read(record)


@router.delete("/{import_id}")
def delete_import(import_id: int, db: Session = Depends(get_db)):
    if not import_repository.delete_import(db, import_id):
        raise HTTPException(status_code=404, detail="Import non trovato")
    return {"status": "deleted", "id": import_id}
