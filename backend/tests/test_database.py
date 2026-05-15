from __future__ import annotations

from pathlib import Path


def test_sqlite_temp_database_creation(tmp_path: Path, sample_payload: dict) -> None:
    from app import database
    from app.repositories.valuation_repository import create_valuation, list_valuations
    from app.schemas.auction_schema import AuctionValuationRequest
    from app.services.scoring_service import valuate_auction

    db_path = tmp_path / "temp.db"
    database.configure_database(f"sqlite:///{db_path}")
    database.init_db()

    db = database.SessionLocal()
    try:
        payload = AuctionValuationRequest(**sample_payload)
        result = valuate_auction(payload)
        create_valuation(db, payload, result)
        assert db_path.exists()
        assert len(list_valuations(db)) == 1
    finally:
        db.close()
        database.Base.metadata.drop_all(bind=database.engine)
