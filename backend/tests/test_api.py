from __future__ import annotations

import sys
from pathlib import Path

import fitz
from fastapi.testclient import TestClient

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.app.main import app

client = TestClient(app)


def _sample_pdf_bytes(text: str = "Immobile libero. Nessun abuso indicato.") -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), text)
    data = doc.tobytes()
    doc.close()
    return data


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_valuate() -> None:
    response = client.post(
        "/valuate",
        json={
            "city": "Torino",
            "zone": "San Donato",
            "address": "Via esempio 10",
            "minimum_bid": 90000,
            "surface_sqm": 80,
            "estimated_market_price_per_sqm": 2500,
            "renovation_cost": 25000,
            "other_costs": 8000,
            "expected_monthly_rent": 850,
            "occupation_status": "libero",
            "legal_risk": "medio",
            "technical_risk": "basso",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["score"] > 0
    assert body["recommendation"]


def test_parse_import_text() -> None:
    response = client.post(
        "/imports/parse",
        json={
            "text": "Tribunale di Torino. Lotto 1. Comune di Torino, Via Roma 10. "
            "Prezzo base euro 120.000. Offerta minima euro 90.000. Superficie 80 mq. "
            "Data asta 30/05/2026. Immobile libero.",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["parsed_fields"]["city"] == "Torino"
    assert body["parsed_fields"]["minimum_bid"] == 90000


def test_import_pdf() -> None:
    response = client.post(
        "/imports/pdf",
        files={"file": ("sample.pdf", _sample_pdf_bytes(), "application/pdf")},
    )
    assert response.status_code == 200
    assert response.json()["page_count"] == 1


def test_document_upload() -> None:
    response = client.post(
        "/documents/upload",
        files={"file": ("perizia.pdf", _sample_pdf_bytes("Immobile occupato con abuso."), "application/pdf")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["risk_level"] in {"basso", "medio", "alto"}
    assert "occupato" in body["red_flags"]
