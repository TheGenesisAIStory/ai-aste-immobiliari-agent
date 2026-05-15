from __future__ import annotations

import json
from typing import List, Optional

from sqlalchemy.orm import Session

from app import models
from app.schemas.auction_schema import AuctionValuationRequest, AuctionValuationResponse


def create_valuation(
    db: Session,
    payload: AuctionValuationRequest,
    result: AuctionValuationResponse,
) -> models.Valuation:
    market_value = result.estimated_market_value
    total_cost = result.total_investment
    gross_margin = market_value - total_cost
    gross_roi = (gross_margin / total_cost * 100) if total_cost else 0.0

    record = models.Valuation(
        city=payload.city,
        zone=payload.zone,
        address=payload.address,
        minimum_bid=payload.minimum_bid,
        surface_sqm=payload.surface_sqm,
        estimated_market_price_per_sqm=payload.estimated_market_price_per_sqm,
        renovation_cost=payload.renovation_cost,
        other_costs=payload.other_costs,
        expected_monthly_rent=payload.expected_monthly_rent,
        occupation_status=payload.occupation_status,
        legal_risk=payload.legal_risk,
        technical_risk=payload.technical_risk,
        market_value_estimate=round(market_value, 2),
        total_cost=round(total_cost, 2),
        gross_margin=round(gross_margin, 2),
        gross_roi=round(gross_roi, 2),
        rental_yield=result.gross_yield_percent,
        score=result.score,
        recommendation=result.recommendation,
        confidence=result.confidence,
        notes=json.dumps(result.notes, ensure_ascii=False),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def list_valuations(db: Session) -> List[models.Valuation]:
    return db.query(models.Valuation).order_by(models.Valuation.created_at.desc()).all()


def get_valuation(db: Session, valuation_id: int) -> Optional[models.Valuation]:
    return db.query(models.Valuation).filter(models.Valuation.id == valuation_id).first()


def delete_valuation(db: Session, valuation_id: int) -> bool:
    record = get_valuation(db, valuation_id)
    if record is None:
        return False
    db.delete(record)
    db.commit()
    return True
