from __future__ import annotations

from pathlib import Path
import sys

import fitz
import pytest
from fastapi.testclient import TestClient

ROOT_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT_DIR / "backend"
for path in (ROOT_DIR, BACKEND_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


@pytest.fixture()
def client(tmp_path: Path):
    from app.database import Base, configure_database, engine, init_db
    from backend.app.main import app

    db_path = tmp_path / "test.db"
    configure_database(f"sqlite:///{db_path}")
    Base.metadata.drop_all(bind=engine)
    init_db()
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def sample_payload() -> dict:
    return {
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
    }


def make_pdf_bytes(text: str = "Immobile libero. Nessun abuso indicato.") -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_textbox((72, 72, 520, 760), text, fontsize=11)
    data = doc.tobytes()
    doc.close()
    return data
