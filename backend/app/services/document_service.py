from __future__ import annotations

import uuid
from pathlib import Path

import fitz

BASE_DIR = Path(__file__).resolve().parents[3]
DOC_DIR = BASE_DIR / "data" / "raw" / "documents"
DOC_DIR.mkdir(parents=True, exist_ok=True)


def save_pdf(file_bytes: bytes, filename: str) -> tuple[str, str]:
    document_id = uuid.uuid4().hex
    safe_name = f"doc_{document_id}.pdf"
    path = DOC_DIR / safe_name
    with open(path, "wb") as f:
        f.write(file_bytes)
    return document_id, str(path)


def extract_text(path: str) -> tuple[str, int]:
    doc = fitz.open(path)
    texts = []
    for page in doc:
        texts.append(page.get_text())
    return "\n".join(texts), len(doc)


def chunk_text(text: str, size: int = 1000) -> list[str]:
    return [text[i : i + size] for i in range(0, len(text), size)]
