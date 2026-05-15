from __future__ import annotations

import os
from dataclasses import dataclass
from io import BytesIO
from typing import List, Optional

import fitz


@dataclass
class OCRResult:
    text: str
    ocr_used: bool
    ocr_pages: List[int]
    text_extraction_method: str
    warnings: List[str]


def ocr_max_pages() -> int:
    try:
        return max(0, int(os.getenv("OCR_MAX_PAGES", "10")))
    except ValueError:
        return 10


def _load_ocr_tools():
    try:
        import pytesseract  # type: ignore
        from PIL import Image  # type: ignore

        return pytesseract, Image, None
    except Exception as exc:  # pragma: no cover - depends on optional install
        return None, None, f"OCR non disponibile: installare Tesseract ({exc})"


def extract_text_with_optional_ocr(path: str, min_chars_per_page: int = 30) -> OCRResult:
    doc = fitz.open(path)
    page_texts: List[str] = []
    ocr_pages: List[int] = []
    warnings: List[str] = []
    ocr_attempted = 0
    native_pages = 0

    pytesseract, Image, load_warning = _load_ocr_tools()

    for index, page in enumerate(doc, start=1):
        native_text = page.get_text() or ""
        if native_text.strip():
            native_pages += 1

        if len(native_text.strip()) >= min_chars_per_page:
            page_texts.append(native_text)
            continue

        if ocr_attempted >= ocr_max_pages():
            page_texts.append(native_text)
            continue

        if pytesseract is None or Image is None:
            if load_warning and load_warning not in warnings:
                warnings.append(load_warning)
            page_texts.append(native_text)
            continue

        try:
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
            image = Image.open(BytesIO(pix.tobytes("png")))
            ocr_text = pytesseract.image_to_string(image, lang=os.getenv("OCR_LANG", "ita+eng"))
            combined = "\n".join(part for part in [native_text, ocr_text] if part.strip())
            page_texts.append(combined)
            if ocr_text.strip():
                ocr_pages.append(index)
            ocr_attempted += 1
        except Exception as exc:  # pragma: no cover - system OCR varies
            warnings.append(f"OCR non disponibile: installare Tesseract ({exc})")
            page_texts.append(native_text)

    ocr_used = bool(ocr_pages)
    if ocr_used and native_pages:
        method = "hybrid"
    elif ocr_used:
        method = "ocr"
    else:
        method = "native"

    return OCRResult(
        text="\n".join(page_texts),
        ocr_used=ocr_used,
        ocr_pages=ocr_pages,
        text_extraction_method=method,
        warnings=warnings,
    )

