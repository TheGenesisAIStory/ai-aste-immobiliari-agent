from __future__ import annotations

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
    gross_annual_rent: float
    gross_yield_percent: float
    score: float
    recommendation: str
    risk_level: str
    notes: List[str]
