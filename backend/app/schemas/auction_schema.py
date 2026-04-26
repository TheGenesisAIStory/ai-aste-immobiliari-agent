from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class AuctionValuationRequest(BaseModel):
    city: str = Field(min_length=1)
    zone: Optional[str] = None
    address: Optional[str] = None
    minimum_bid: float = Field(gt=0)
    surface_sqm: float = Field(gt=0)
    estimated_market_price_per_sqm: float = Field(gt=0)
    renovation_cost: float = Field(default=0, ge=0)
    other_costs: float = Field(default=0, ge=0)
    expected_monthly_rent: float = Field(default=0, ge=0)
    occupation_status: str = "sconosciuto"
    legal_risk: str = "medio"
    technical_risk: str = "medio"


class AuctionValuationResponse(BaseModel):
    city: str
    zone: Optional[str]
    address: Optional[str]
    total_investment: float
    estimated_market_value: float
    discount_percent: float
    gross_margin: float
    gross_roi_percent: float
    gross_annual_rent: float
    gross_yield_percent: float
    score: float
    recommendation: str
    risk_level: str
    confidence: str
    notes: List[str]


class ValuationRead(BaseModel):
    id: int
    city: str
    zone: Optional[str]
    address: Optional[str]
    minimum_bid: float
    surface_sqm: float
    estimated_market_price_per_sqm: float
    renovation_cost: float
    other_costs: float
    expected_monthly_rent: float
    occupation_status: str
    legal_risk: str
    technical_risk: str
    market_value_estimate: float
    total_cost: float
    gross_margin: float
    gross_roi: float
    rental_yield: float
    score: float
    recommendation: str
    confidence: str
    notes: List[str]
    created_at: datetime
    updated_at: datetime
