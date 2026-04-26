from __future__ import annotations

import json
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories import valuation_repository
from app.schemas.auction_schema import AuctionValuationRequest, ValuationRead
from app.services.scoring_service import valuate_auction

router = APIRouter(prefix="/valuations", tags=["valuations"])


def _to_read(record) -> ValuationRead:
    now = datetime.utcnow()
    return ValuationRead(
        id=record.id,
        city=record.city or "",
        zone=record.zone,
        address=record.address,
        minimum_bid=record.minimum_bid or 0,
        surface_sqm=record.surface_sqm or 0,
        estimated_market_price_per_sqm=record.estimated_market_price_per_sqm or 0,
        renovation_cost=record.renovation_cost or 0,
        other_costs=record.other_costs or 0,
        expected_monthly_rent=record.expected_monthly_rent or 0,
        occupation_status=record.occupation_status or "sconosciuto",
        legal_risk=record.legal_risk or "medio",
        technical_risk=record.technical_risk or "medio",
        market_value_estimate=record.market_value_estimate or 0,
        total_cost=record.total_cost or 0,
        gross_margin=record.gross_margin or 0,
        gross_roi=record.gross_roi or 0,
        rental_yield=record.rental_yield or getattr(record, "roi", None) or 0,
        score=record.score or 0,
        recommendation=record.recommendation or "sconosciuto",
        confidence=record.confidence or "bassa",
        notes=json.loads(record.notes or "[]"),
        created_at=record.created_at or now,
        updated_at=record.updated_at or now,
    )


@router.post("", response_model=ValuationRead)
def create_valuation(payload: AuctionValuationRequest, db: Session = Depends(get_db)):
    result = valuate_auction(payload)
    record = valuation_repository.create_valuation(db, payload, result)
    return _to_read(record)


@router.get("", response_model=List[ValuationRead])
def list_valuations(db: Session = Depends(get_db)):
    return [_to_read(record) for record in valuation_repository.list_valuations(db)]


@router.get("/{valuation_id}", response_model=ValuationRead)
def get_valuation(valuation_id: int, db: Session = Depends(get_db)):
    record = valuation_repository.get_valuation(db, valuation_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Valutazione non trovata")
    return _to_read(record)


@router.delete("/{valuation_id}")
def delete_valuation(valuation_id: int, db: Session = Depends(get_db)):
    if not valuation_repository.delete_valuation(db, valuation_id):
        raise HTTPException(status_code=404, detail="Valutazione non trovata")
    return {"status": "deleted", "id": valuation_id}
