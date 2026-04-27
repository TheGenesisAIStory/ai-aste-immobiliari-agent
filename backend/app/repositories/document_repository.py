from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app import models


def create_document_analysis(
    db: Session,
    filename: str,
    saved_path: str,
    page_count: int,
    text_preview: str,
    analysis: Dict[str, Any],
) -> models.DocumentAnalysis:
    record = models.DocumentAnalysis(
        filename=filename,
        saved_path=saved_path,
        page_count=page_count,
        extracted_text_preview=text_preview,
        summary=analysis.get("summary", ""),
        extracted_fields_json=json.dumps(analysis.get("extracted_fields", {}), ensure_ascii=False),
        red_flags_json=json.dumps(analysis.get("red_flags", []), ensure_ascii=False),
        missing_fields_json=json.dumps(analysis.get("missing_fields", []), ensure_ascii=False),
        confidence=analysis.get("confidence", "bassa"),
        analysis_mode=analysis.get("analysis_mode", "rule_based"),
        ocr_used="true" if analysis.get("ocr_used") else "false",
        ocr_pages_json=json.dumps(analysis.get("ocr_pages", []), ensure_ascii=False),
        text_extraction_method=analysis.get("text_extraction_method", "native"),
        warnings_json=json.dumps(analysis.get("warnings", []), ensure_ascii=False),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def list_documents(db: Session) -> List[models.DocumentAnalysis]:
    return db.query(models.DocumentAnalysis).order_by(models.DocumentAnalysis.created_at.desc()).all()


def get_document(db: Session, document_id: int) -> Optional[models.DocumentAnalysis]:
    return db.query(models.DocumentAnalysis).filter(models.DocumentAnalysis.id == document_id).first()


def delete_document(db: Session, document_id: int) -> bool:
    record = get_document(db, document_id)
    if record is None:
        return False
    db.delete(record)
    db.commit()
    return True
