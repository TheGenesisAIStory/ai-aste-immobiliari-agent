from __future__ import annotations

import os
import re
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

import requests
from bs4 import BeautifulSoup

try:
    import fitz  # PyMuPDF
except Exception:  # pragma: no cover
    fitz = None

BASE_DIR = Path(__file__).resolve().parents[3]
RAW_IMPORTS_DIR = BASE_DIR / "data" / "raw" / "imports"
RAW_IMPORTS_DIR.mkdir(parents=True, exist_ok=True)

USER_AGENT = "AI-Aste-Agent/1.0 (+single-page-import; no-crawling)"


@dataclass
class ImportResult:
    import_id: str
    saved_path: str
    text: str
    page_count: Optional[int] = None
    status_code: Optional[int] = None
    content_type: Optional[str] = None
    final_url: Optional[str] = None
    source_kind: str = "html"


def import_timeout() -> int:
    try:
        return int(os.getenv("IMPORT_TIMEOUT_SECONDS", "20"))
    except ValueError:
        return 20


def import_max_mb() -> int:
    try:
        return int(os.getenv("IMPORT_MAX_MB", "15"))
    except ValueError:
        return 15


def _safe_filename(name: str) -> str:
    name = name.strip().replace(" ", "_")
    name = re.sub(r"[^A-Za-z0-9_\-.]", "", name)
    return name[:200] or "file"


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", errors="ignore")


def _write_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def _clean_html_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "nav", "footer", "header", "svg"]):
        tag.decompose()
    text = soup.get_text(separator=" ")
    return re.sub(r"\s+", " ", text or "").strip()


def _check_size(content: bytes, max_mb: Optional[int] = None) -> None:
    limit = max_mb or import_max_mb()
    if len(content) > limit * 1024 * 1024:
        raise ValueError(f"Download troppo grande (max {limit}MB)")


def import_from_pdf(filename: str, content: bytes, max_mb: Optional[int] = None) -> Tuple[str, str, str, int]:
    if fitz is None:  # pragma: no cover
        raise RuntimeError("PyMuPDF non disponibile")
    if not filename.lower().endswith(".pdf"):
        raise ValueError("Formato file non valido: solo PDF")
    _check_size(content, max_mb)

    import_id = uuid.uuid4().hex
    path = RAW_IMPORTS_DIR / _safe_filename(f"pdf_{import_id}.pdf")
    _write_bytes(path, content)

    doc = fitz.open(stream=content, filetype="pdf")
    texts = [page.get_text() for page in doc]
    text = "\n".join(texts)
    page_count = len(doc)
    _write_text(RAW_IMPORTS_DIR / _safe_filename(f"pdf_{import_id}.txt"), text)
    return import_id, str(path), text, page_count


def import_from_url_advanced(source_url: str) -> ImportResult:
    headers = {"User-Agent": USER_AGENT, "Accept": "text/html,application/pdf;q=0.9,*/*;q=0.2"}
    try:
        response = requests.get(source_url, headers=headers, timeout=import_timeout(), allow_redirects=True, stream=True)
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"Errore HTTP: {exc}") from exc

    raw_content = getattr(response, "content", None)
    content = raw_content if isinstance(raw_content, bytes) else (response.text or "").encode("utf-8")
    _check_size(content)
    response_headers = getattr(response, "headers", {}) or {}
    headers = response_headers if isinstance(response_headers, dict) else {}
    content_type = headers.get("content-type", "").split(";")[0].strip().lower()
    response_url = getattr(response, "url", source_url)
    final_url = response_url if isinstance(response_url, str) else source_url
    response_status = getattr(response, "status_code", None)
    status_code = response_status if isinstance(response_status, int) else None

    if content_type == "application/pdf" or final_url.lower().endswith(".pdf"):
        import_id, path, text, pages = import_from_pdf("url_download.pdf", content, max_mb=import_max_mb())
        return ImportResult(
            import_id=import_id,
            saved_path=path,
            text=text,
            page_count=pages,
            status_code=status_code,
            content_type=content_type,
            final_url=final_url,
            source_kind="pdf_url",
        )

    html = response.text
    text = _clean_html_text(html)
    import_id = uuid.uuid4().hex
    path = RAW_IMPORTS_DIR / _safe_filename(f"url_{import_id}.html")
    _write_text(path, html)
    _write_text(RAW_IMPORTS_DIR / _safe_filename(f"url_{import_id}.txt"), text)
    return ImportResult(
        import_id=import_id,
        saved_path=str(path),
        text=text,
        status_code=status_code,
        content_type=content_type,
        final_url=final_url,
        source_kind="html",
    )


def import_from_url(source_url: str, timeout: int = 10) -> Tuple[str, str, str]:
    result = import_from_url_advanced(source_url)
    return result.import_id, result.saved_path, result.text
