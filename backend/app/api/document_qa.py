from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories import document_repository
from typing import List

from app.schemas.rag_schema import DocumentChunkRead, DocumentQuestionRequest, DocumentQuestionResponse
from app.services import rag_service

router = APIRouter(prefix="/documents", tags=["document-qa"])


@router.post("/{document_id}/ask", response_model=DocumentQuestionResponse)
def ask_document(document_id: int, payload: DocumentQuestionRequest, db: Session = Depends(get_db)):
    if document_repository.get_document(db, document_id) is None:
        raise HTTPException(status_code=404, detail="Documento non trovato")
    return rag_service.answer_question(document_id, payload.question)


@router.get("/{document_id}/chunks", response_model=List[DocumentChunkRead])
def get_document_chunks(document_id: int, db: Session = Depends(get_db)):
    if document_repository.get_document(db, document_id) is None:
        raise HTTPException(status_code=404, detail="Documento non trovato")
    return rag_service.get_chunks(document_id)


@router.post("/{document_id}/reindex")
def reindex_document(document_id: int, db: Session = Depends(get_db)):
    record = document_repository.get_document(db, document_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Documento non trovato")
    text = record.extracted_text_preview or record.summary or ""
    chunks = rag_service.save_chunks(document_id, text)
    return {"status": "ok", "document_id": document_id, "chunks": len(chunks)}
