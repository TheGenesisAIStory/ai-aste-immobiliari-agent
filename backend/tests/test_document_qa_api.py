from __future__ import annotations

from pathlib import Path

from backend.tests.conftest import make_pdf_bytes


def test_document_qa_endpoints_and_delete_chunks(client) -> None:
    response = client.post(
        "/documents/upload",
        files={"file": ("qa.pdf", make_pdf_bytes("Immobile occupato. Offerta minima euro 90.000."), "application/pdf")},
    )
    assert response.status_code == 200
    document_id = response.json()["id"]

    chunks = client.get(f"/documents/{document_id}/chunks")
    assert chunks.status_code == 200
    assert len(chunks.json()) > 0

    ask = client.post(f"/documents/{document_id}/ask", json={"question": "L'immobile è occupato?"})
    assert ask.status_code == 200
    assert ask.json()["mode"] == "keyword_rag"

    reindex = client.post(f"/documents/{document_id}/reindex")
    assert reindex.status_code == 200

    deleted = client.delete(f"/documents/{document_id}")
    assert deleted.status_code == 200
    assert deleted.json()["deleted_chunks"] >= 0


def test_delete_document_missing_file_does_not_crash(client) -> None:
    response = client.post(
        "/documents/upload",
        files={"file": ("missing.pdf", make_pdf_bytes("Immobile libero."), "application/pdf")},
    )
    document_id = response.json()["id"]
    saved_path = response.json()["saved_path"]
    Path(saved_path).unlink()

    deleted = client.delete(f"/documents/{document_id}")
    assert deleted.status_code == 200
    assert deleted.json()["deleted_file"] is False

