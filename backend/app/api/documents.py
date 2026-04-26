from __future__ import annotations

import json
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories import document_repository
from app.schemas.document_schema import DocumentAnalysis, DocumentAnalysisRead
from app.services.document_agent import analyze_document
from app.services.document_service import chunk_text, extract_text, save_pdf

router = APIRouter(prefix="/documents", tags=["documents"])


def _to_read(record) -> DocumentAnalysisRead:
    return DocumentAnalysisRead(
        id=record.id,
        filename=record.filename,
        saved_path=record.saved_path,
        page_count=record.page_count,
        extracted_text_preview=record.extracted_text_preview,
        summary=record.summary,
        extracted_fields=json.loads(record.extracted_fields_json or "{}"),
        red_flags=json.loads(record.red_flags_json or "[]"),
        missing_fields=json.loads(record.missing_fields_json or "[]"),
        confidence=record.confidence,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


@router.post("/upload", response_model=DocumentAnalysis)
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    try:
        doc_id, path = save_pdf(content, file.filename)
        text, pages = extract_text(path)
        chunks = chunk_text(text)
        analysis = analyze_document(text)
        record = document_repository.create_document_analysis(
            db=db,
            filename=file.filename,
            saved_path=path,
            page_count=pages,
            text_preview=text[:500],
            analysis=analysis,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Errore analisi documento: {exc}") from exc

    return {
        "id": record.id,
        "document_id": doc_id,
        "filename": file.filename,
        "status": "ok",
        "page_count": pages,
        "saved_path": path,
        "text_preview": text[:500],
        "chunks": [
            {"index": i, "text_preview": c[:200], "char_count": len(c)}
            for i, c in enumerate(chunks)
        ],
        "summary": analysis["summary"],
        "extracted_fields": analysis["extracted_fields"],
        "extracted_sections": analysis["sections"],
        "red_flags": analysis["red_flags"],
        "missing_fields": analysis["missing_fields"],
        "risk_level": analysis["risk_level"],
        "confidence": analysis["confidence"],
        "valuation_draft": analysis["valuation_draft"],
        "notes": analysis["notes"],
    }


@router.get("", response_model=List[DocumentAnalysisRead])
def list_documents(db: Session = Depends(get_db)):
    return [_to_read(record) for record in document_repository.list_documents(db)]


@router.get("/{document_id}", response_model=DocumentAnalysisRead)
def get_document(document_id: int, db: Session = Depends(get_db)):
    record = document_repository.get_document(db, document_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Documento non trovato")
    return _to_read(record)


@router.delete("/{document_id}")
def delete_document(document_id: int, db: Session = Depends(get_db)):
    if not document_repository.delete_document(db, document_id):
        raise HTTPException(status_code=404, detail="Documento non trovato")
    return {"status": "deleted", "id": document_id}
