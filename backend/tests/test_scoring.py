from __future__ import annotations

from app.schemas.auction_schema import AuctionValuationRequest
from app.services.scoring_service import valuate_auction


def test_valuate_auction_calculates_metrics(sample_payload: dict) -> None:
    result = valuate_auction(AuctionValuationRequest(**sample_payload))

    assert result.estimated_market_value == 200000
    assert result.total_investment == 123000
    assert result.gross_margin == 77000
    assert result.score > 0
    assert result.recommendation


def test_health_and_valuate_do_not_persist(client, sample_payload: dict) -> None:
    assert client.get("/health").json() == {"status": "ok"}

    response = client.post("/valuate", json=sample_payload)
    assert response.status_code == 200
    assert client.get("/valuations").json() == []
