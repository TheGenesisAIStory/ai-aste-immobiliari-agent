from __future__ import annotations

import json
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories import document_repository
from app.schemas.document_schema import DocumentAnalysis, DocumentAnalysisRead
from app.services import rag_service
from app.services.document_agent import analyze_document
from app.services.document_service import chunk_text, extract_text_with_metadata, save_pdf

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
        analysis_mode=record.analysis_mode or "rule_based",
        ocr_used=(record.ocr_used == "true"),
        ocr_pages=json.loads(record.ocr_pages_json or "[]"),
        text_extraction_method=record.text_extraction_method or "native",
        warnings=json.loads(record.warnings_json or "[]"),
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


@router.post("/upload", response_model=DocumentAnalysis)
async def upload_document(
    file: UploadFile = File(...),
    use_llm: bool = Form(True),
    db: Session = Depends(get_db),
):
    content = await file.read()
    try:
        doc_id, path = save_pdf(content, file.filename)
        text, pages, ocr_result = extract_text_with_metadata(path)
        chunks = chunk_text(text)
        ocr_metadata = {
            "ocr_used": ocr_result.ocr_used,
            "ocr_pages": ocr_result.ocr_pages,
            "text_extraction_method": ocr_result.text_extraction_method,
            "warnings": ocr_result.warnings,
        }
        analysis = analyze_document(text, document_id=doc_id, filename=file.filename, ocr_metadata=ocr_metadata, use_llm=use_llm)
        record = document_repository.create_document_analysis(
            db=db,
            filename=file.filename,
            saved_path=path,
            page_count=pages,
            text_preview=text[:500],
            analysis=analysis,
        )
        rag_chunks = rag_service.save_chunks(record.id, text)
        analysis["rag_available"] = bool(rag_chunks)
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
        "analysis_mode": analysis["analysis_mode"],
        "fields": analysis["fields"],
        "extracted_fields": analysis["extracted_fields"],
        "extracted_sections": analysis["sections"],
        "red_flags": analysis["red_flags"],
        "missing_fields": analysis["missing_fields"],
        "risk_level": analysis["risk_level"],
        "confidence": analysis["confidence"],
        "ocr_used": analysis["ocr_used"],
        "ocr_pages": analysis["ocr_pages"],
        "text_extraction_method": analysis["text_extraction_method"],
        "warnings": analysis["warnings"],
        "rag_available": analysis["rag_available"],
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
    record = document_repository.get_document(db, document_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Documento non trovato")
    deleted_file = False
    if record.saved_path:
        path = Path(record.saved_path)
        if path.exists():
            path.unlink()
            deleted_file = True
    deleted_chunks = rag_service.delete_chunks(document_id)
    document_repository.delete_document(db, document_id)
    return {
        "status": "deleted",
        "id": document_id,
        "deleted_record": True,
        "deleted_file": deleted_file,
        "deleted_chunks": deleted_chunks,
    }
