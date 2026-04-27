from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from backend.tests.conftest import make_pdf_bytes


def test_import_url_html_metadata() -> None:
    from app.services.import_service import import_from_url_advanced

    mocked = Mock()
    mocked.text = "<html><body><script>x</script>Comune di Torino</body></html>"
    mocked.content = mocked.text.encode("utf-8")
    mocked.headers = {"content-type": "text/html; charset=utf-8"}
    mocked.status_code = 200
    mocked.url = "https://example.com/final"
    mocked.raise_for_status.return_value = None

    with patch("app.services.import_service.requests.get", return_value=mocked):
        result = import_from_url_advanced("https://example.com")

    assert result.status_code == 200
    assert result.content_type == "text/html"
    assert result.final_url == "https://example.com/final"
    assert "Comune di Torino" in result.text
    assert "script" not in result.text


def test_import_url_pdf_content_type() -> None:
    from app.services.import_service import import_from_url_advanced

    mocked = Mock()
    mocked.text = ""
    mocked.content = make_pdf_bytes("Offerta minima euro 90.000.")
    mocked.headers = {"content-type": "application/pdf"}
    mocked.status_code = 200
    mocked.url = "https://example.com/file.pdf"
    mocked.raise_for_status.return_value = None

    with patch("app.services.import_service.requests.get", return_value=mocked):
        result = import_from_url_advanced("https://example.com/file.pdf")

    assert result.source_kind == "pdf_url"
    assert result.page_count == 1


def test_import_max_size(monkeypatch) -> None:
    from app.services.import_service import _check_size

    monkeypatch.setenv("IMPORT_MAX_MB", "1")
    with pytest.raises(ValueError):
        _check_size(b"x" * (2 * 1024 * 1024))
