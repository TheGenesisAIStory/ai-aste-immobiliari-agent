from __future__ import annotations

from backend.tests.conftest import make_pdf_bytes


def test_ocr_fallback_when_tesseract_unavailable(tmp_path, monkeypatch) -> None:
    from app.services import ocr_service

    pdf_path = tmp_path / "scan.pdf"
    pdf_path.write_bytes(make_pdf_bytes(""))
    monkeypatch.setattr(ocr_service, "_load_ocr_tools", lambda: (None, None, "OCR non disponibile: installare Tesseract"))

    result = ocr_service.extract_text_with_optional_ocr(str(pdf_path))

    assert result.ocr_used is False
    assert result.text_extraction_method == "native"
    assert "OCR non disponibile" in result.warnings[0]

