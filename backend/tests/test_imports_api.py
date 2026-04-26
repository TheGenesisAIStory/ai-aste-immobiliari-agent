from __future__ import annotations

from unittest.mock import Mock, patch

from backend.tests.conftest import make_pdf_bytes


def test_import_url_with_mock_requests(client) -> None:
    html = """
    <html><body>
    Tribunale di Torino. Lotto 1. Comune di Torino, Via Roma 10.
    Prezzo base euro 120.000. Offerta minima euro 90.000.
    Superficie 80 mq. Data asta 30/05/2026. Immobile libero.
    </body></html>
    """
    mocked_response = Mock()
    mocked_response.text = html
    mocked_response.raise_for_status.return_value = None

    with patch("app.services.import_service.requests.get", return_value=mocked_response):
        response = client.post("/imports/url", json={"source_url": "https://example.com/asta"})

    assert response.status_code == 200
    body = response.json()
    assert body["id"] is not None
    assert body["parsed_fields"]["city"] == "Torino"
    assert body["parsed_fields"]["minimum_bid"] == 90000

    listed = client.get("/imports").json()
    assert len(listed) == 1
    assert client.get(f"/imports/{listed[0]['id']}").status_code == 200
    assert client.delete(f"/imports/{listed[0]['id']}").status_code == 200
    assert client.get(f"/imports/{listed[0]['id']}").status_code == 404


def test_import_pdf_persists(client) -> None:
    response = client.post(
        "/imports/pdf",
        files={"file": ("sample.pdf", make_pdf_bytes("Comune di Torino. Offerta minima euro 90.000. Superficie 80 mq."), "application/pdf")},
    )
    assert response.status_code == 200
    assert response.json()["page_count"] == 1
    assert len(client.get("/imports").json()) == 1


def test_import_404(client) -> None:
    assert client.get("/imports/999").status_code == 404
    assert client.delete("/imports/999").status_code == 404
