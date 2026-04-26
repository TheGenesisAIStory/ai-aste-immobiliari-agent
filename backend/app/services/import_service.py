from __future__ import annotations

import os
import re
import uuid
from pathlib import Path
from typing import Tuple

import requests
from bs4 import BeautifulSoup

try:
    import fitz  # PyMuPDF
except Exception:  # pragma: no cover
    fitz = None

BASE_DIR = Path(__file__).resolve().parents[3]
RAW_IMPORTS_DIR = BASE_DIR / "data" / "raw" / "imports"
RAW_IMPORTS_DIR.mkdir(parents=True, exist_ok=True)

USER_AGENT = "AI-Aste-Agent/1.0 (single-page import; no crawling)"


def _safe_filename(name: str) -> str:
    name = name.strip().replace(" ", "_")
    name = re.sub(r"[^A-Za-z0-9_\-.]", "", name)
    return name[:200] or "file"


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", errors="ignore")


def _preview(text: str, n: int = 500) -> str:
    text = re.sub(r"\s+", " ", text or "").strip()
    return text[:n]


def import_from_url(source_url: str, timeout: int = 10) -> Tuple[str, str, str]:
    """Download a single page and save raw HTML + extracted text.

    Returns: (import_id, saved_html_path, extracted_text)
    """
    headers = {"User-Agent": USER_AGENT}
    try:
        resp = requests.get(source_url, headers=headers, timeout=timeout)
        resp.raise_for_status()
    except requests.exceptions.RequestException as exc:  # pragma: no cover
        raise RuntimeError(f"Errore HTTP: {exc}") from exc

    html = resp.text
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text(separator=" ")

    import_id = uuid.uuid4().hex
    filename = _safe_filename(f"url_{import_id}.html")
    path = RAW_IMPORTS_DIR / filename
    _write_text(path, html)

    text_path = RAW_IMPORTS_DIR / _safe_filename(f"url_{import_id}.txt")
    _write_text(text_path, text)

    return import_id, str(path), text


def import_from_pdf(filename: str, content: bytes, max_mb: int = 15) -> Tuple[str, str, str, int]:
    if fitz is None:  # pragma: no cover
        raise RuntimeError("PyMuPDF non disponibile")

    if not filename.lower().endswith(".pdf"):
        raise ValueError("Formato file non valido: solo PDF")

    size_mb = len(content) / (1024 * 1024)
    if size_mb > max_mb:
        raise ValueError("File troppo grande (max 15MB)")

    import_id = uuid.uuid4().hex
    safe = _safe_filename(f"pdf_{import_id}.pdf")
    path = RAW_IMPORTS_DIR / safe
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(content)

    doc = fitz.open(stream=content, filetype="pdf")
    texts = []
    for page in doc:
        try:
            texts.append(page.get_text())
        except Exception:  # pragma: no cover
            continue
    text = "\n".join(texts)
    page_count = len(doc)

    text_path = RAW_IMPORTS_DIR / _safe_filename(f"pdf_{import_id}.txt")
    _write_text(text_path, text)

    return import_id, str(path), text, page_count
