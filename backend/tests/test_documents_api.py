from __future__ import annotations

from backend.tests.conftest import make_pdf_bytes


def test_document_upload_list_detail_delete(client) -> None:
    pdf_text = (
        "Tribunale di Torino. Comune di Torino, Via Roma 10. Superficie 80 mq. "
        "Offerta minima euro 90.000. Data asta 30/05/2026. "
        "Immobile occupato con abuso edilizio."
    )
    response = client.post(
        "/documents/upload",
        files={"file": ("perizia.pdf", make_pdf_bytes(pdf_text), "application/pdf")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["id"] is not None
    assert body["summary"]
    assert body["red_flags"][0]["category"]

    docs = client.get("/documents").json()
    assert len(docs) == 1
    doc_id = docs[0]["id"]
    assert client.get(f"/documents/{doc_id}").status_code == 200
    assert client.delete(f"/documents/{doc_id}").status_code == 200
    assert client.get(f"/documents/{doc_id}").status_code == 404


def test_document_404(client) -> None:
    assert client.get("/documents/999").status_code == 404
    assert client.delete("/documents/999").status_code == 404
