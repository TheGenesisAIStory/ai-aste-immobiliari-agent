from __future__ import annotations

import uuid
import os
import re
from pathlib import Path
from typing import List, Tuple

import fitz

BASE_DIR = Path(__file__).resolve().parents[3]
DOC_DIR = BASE_DIR / "data" / "raw" / "documents"
DOC_DIR.mkdir(parents=True, exist_ok=True)


def max_upload_mb() -> int:
    try:
        return int(os.getenv("MAX_UPLOAD_MB", "15"))
    except ValueError:
        return 15


def validate_pdf(filename: str, file_bytes: bytes) -> None:
    if not filename.lower().endswith(".pdf"):
        raise ValueError("Solo PDF consentiti")
    if len(file_bytes) > max_upload_mb() * 1024 * 1024:
        raise ValueError(f"File troppo grande (max {max_upload_mb()}MB)")


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def save_pdf(file_bytes: bytes, filename: str) -> Tuple[str, str]:
    validate_pdf(filename, file_bytes)
    document_id = uuid.uuid4().hex
    safe_name = f"doc_{document_id}.pdf"
    path = DOC_DIR / safe_name
    with open(path, "wb") as f:
        f.write(file_bytes)
    return document_id, str(path)


def extract_text(path: str) -> Tuple[str, int]:
    doc = fitz.open(path)
    texts = []
    for page in doc:
        texts.append(page.get_text())
    return normalize_text("\n".join(texts)), len(doc)


def chunk_text(text: str, size: int = 1000) -> List[str]:
    return [text[i : i + size] for i in range(0, len(text), size)]
