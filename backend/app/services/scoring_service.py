from __future__ import annotations

from typing import Optional

from app.schemas.auction_schema import AuctionValuationRequest, AuctionValuationResponse

RISK_WEIGHTS = {
    "basso": 5,
    "medio": 15,
    "alto": 30,
    "sconosciuto": 20,
}


def _risk_penalty(value: Optional[str]) -> int:
    normalized = (value or "sconosciuto").strip().lower()
    return RISK_WEIGHTS.get(normalized, 20)


def _recommend(score: float) -> str:
    if score >= 75:
        return "approfondisci offerta"
    if score >= 60:
        return "monitora"
    if score >= 45:
        return "approfondisci solo con verifiche"
    return "scarta"


def _risk_level(total_penalty: int) -> str:
    if total_penalty >= 65:
        return "alto"
    if total_penalty >= 35:
        return "medio"
    return "basso"


def valuate_auction(payload: AuctionValuationRequest) -> AuctionValuationResponse:
    estimated_market_value = payload.surface_sqm * payload.estimated_market_price_per_sqm
    total_investment = payload.minimum_bid + payload.renovation_cost + payload.other_costs
    gross_annual_rent = payload.expected_monthly_rent * 12

    discount = 0.0
    if estimated_market_value:
        discount = (estimated_market_value - total_investment) / estimated_market_value * 100

    gross_yield = 0.0
    if total_investment:
        gross_yield = gross_annual_rent / total_investment * 100

    risk_penalty = _risk_penalty(payload.legal_risk) + _risk_penalty(payload.technical_risk)
    if payload.occupation_status.strip().lower() not in {"libero", "vacant"}:
        risk_penalty += 20

    score = 50.0
    score += min(max(discount, -30), 45) * 0.75
    score += min(gross_yield, 12) * 2
    score -= risk_penalty * 0.55
    score = round(max(0, min(100, score)), 1)

    notes = [
        "Valutazione rule-based MVP: verificare sempre perizia, occupazione, vincoli e costi reali.",
    ]
    if discount < 10:
        notes.append("Margine rispetto al valore stimato contenuto.")
    if payload.occupation_status.strip().lower() != "libero":
        notes.append("Stato occupazionale da verificare prima di qualsiasi offerta.")

    return AuctionValuationResponse(
        city=payload.city,
        zone=payload.zone,
        address=payload.address,
        total_investment=round(total_investment, 2),
        estimated_market_value=round(estimated_market_value, 2),
        discount_percent=round(discount, 2),
        gross_annual_rent=round(gross_annual_rent, 2),
        gross_yield_percent=round(gross_yield, 2),
        score=score,
        recommendation=_recommend(score),
        risk_level=_risk_level(risk_penalty),
        notes=notes,
    )
