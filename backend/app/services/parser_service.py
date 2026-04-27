from __future__ import annotations

from typing import Any, Dict, Optional

from app.services.document_agent import detect_red_flags, extract_fields, normalize_text

REQUIRED_PARSED_FIELDS = [
    "city",
    "address",
    "base_price",
    "minimum_bid",
    "surface_sqm",
    "auction_date",
    "court",
    "procedure_number",
    "lot_number",
    "occupation_status",
]


def parse_auction_text(text: str, source_url: Optional[str] = None) -> Dict[str, Any]:
    normalized = normalize_text(text)
    fields = extract_fields(normalized)
    parsed_fields = {
        "city": fields.get("city"),
        "address": fields.get("address"),
        "base_price": fields.get("base_price"),
        "minimum_bid": fields.get("minimum_bid"),
        "surface_sqm": fields.get("surface_sqm"),
        "auction_date": fields.get("auction_date"),
        "court": fields.get("court"),
        "procedure_number": fields.get("procedure_number"),
        "lot_number": fields.get("lot_number"),
        "occupation_status": fields.get("occupation_status"),
        "source_url": source_url,
    }
    missing_fields = [
        field for field in REQUIRED_PARSED_FIELDS if parsed_fields.get(field) in (None, "", "sconosciuto")
    ]
    red_flags = detect_red_flags(normalized)
    risk_keywords = [flag["label"] for flag in red_flags]
    present = len(REQUIRED_PARSED_FIELDS) - len(missing_fields)
    confidence = "alta" if present >= 8 else "media" if present >= 5 else "bassa"

    notes = []
    if not normalized:
        notes.append("Testo vuoto o non leggibile.")
    if missing_fields:
        notes.append("Alcuni campi sono mancanti: completarli manualmente prima della valutazione.")
    if risk_keywords:
        notes.append("Sono state trovate parole chiave di rischio: verificare perizia e avviso di vendita.")

    return {
        "parsed_fields": parsed_fields,
        "missing_fields": missing_fields,
        "risk_keywords": risk_keywords,
        "red_flags": red_flags,
        "confidence": confidence,
        "notes": notes,
    }
