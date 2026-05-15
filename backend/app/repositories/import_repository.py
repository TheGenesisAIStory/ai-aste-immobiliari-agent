from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app import models


def create_import_record(
    db: Session,
    source_type: str,
    saved_path: Optional[str] = None,
    text_preview: str = "",
    parsed: Optional[Dict[str, Any]] = None,
    source_url: Optional[str] = None,
    filename: Optional[str] = None,
    status: str = "ok",
    error_message: Optional[str] = None,
) -> models.ImportRecord:
    parsed = parsed or {}
    record = models.ImportRecord(
        source_type=source_type,
        source_url=source_url,
        filename=filename,
        saved_path=saved_path,
        extracted_text_preview=text_preview,
        parsed_fields_json=json.dumps(parsed.get("parsed_fields", {}), ensure_ascii=False),
        risk_keywords_json=json.dumps(parsed.get("risk_keywords", []), ensure_ascii=False),
        missing_fields_json=json.dumps(parsed.get("missing_fields", []), ensure_ascii=False),
        confidence=parsed.get("confidence", "bassa"),
        status=status,
        error_message=error_message,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def list_imports(db: Session) -> List[models.ImportRecord]:
    return db.query(models.ImportRecord).order_by(models.ImportRecord.created_at.desc()).all()


def get_import(db: Session, import_id: int) -> Optional[models.ImportRecord]:
    return db.query(models.ImportRecord).filter(models.ImportRecord.id == import_id).first()


def delete_import(db: Session, import_id: int) -> bool:
    record = get_import(db, import_id)
    if record is None:
        return False
    db.delete(record)
    db.commit()
    return True
