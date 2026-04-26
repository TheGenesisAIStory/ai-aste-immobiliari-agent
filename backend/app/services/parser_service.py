"""Rule-based MVP parser for Italian real estate auction texts.

No LLM is used here. The goal is to extract a first draft from a single
imported page or PDF and explicitly expose missing fields to the user.
"""
from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict, List, Optional

RISK_KEYWORDS = [
    "occupato",
    "occupata",
    "abuso",
    "abusivo",
    "difformità",
    "difformita",
    "sanatoria",
    "usufrutto",
    "servitù",
    "servitu",
    "pignoramento",
    "ipoteca",
    "sconosciuto",
    "non libero",
    "morosità",
    "morosita",
]

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


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def _parse_italian_amount(value: str) -> Optional[float]:
    cleaned = re.sub(r"[^0-9,\.]", "", value or "").strip(".,")
    if not cleaned:
        return None
    if "," in cleaned and "." in cleaned:
        cleaned = cleaned.replace(".", "").replace(",", ".")
    elif "," in cleaned:
        cleaned = cleaned.replace(",", ".")
    elif re.fullmatch(r"\d{1,3}(?:\.\d{3})+", cleaned):
        cleaned = cleaned.replace(".", "")
    try:
        return float(cleaned)
    except ValueError:
        return None


def _first_amount(patterns: List[str], text: str) -> Optional[float]:
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return _parse_italian_amount(match.group(1))
    return None


def extract_base_price(text: str) -> Optional[float]:
    return _first_amount([
        r"prezzo\s+base(?:\s+d['’]asta)?\s*(?:euro|€|eur)?\s*[:\-]?\s*([0-9\.\,]+)",
        r"base\s+d['’]asta\s*(?:euro|€|eur)?\s*[:\-]?\s*([0-9\.\,]+)",
    ], text)


def extract_minimum_bid(text: str) -> Optional[float]:
    return _first_amount([
        r"offerta\s+minima\s*(?:euro|€|eur)?\s*[:\-]?\s*([0-9\.\,]+)",
        r"prezzo\s+minimo\s*(?:euro|€|eur)?\s*[:\-]?\s*([0-9\.\,]+)",
    ], text)


def extract_surface_sqm(text: str) -> Optional[float]:
    patterns = [
        r"(?:superficie|consistenza|mq|metri\s+quadrati)\s*(?:commerciale)?\s*[:\-]?\s*([0-9]+(?:[\.,][0-9]+)?)\s*(?:mq|m²|metri)",
        r"([0-9]+(?:[\.,][0-9]+)?)\s*(?:mq|m²)\s*(?:commerciali|circa)?",
    ]
    return _first_amount(patterns, text)


def extract_auction_date(text: str) -> Optional[str]:
    patterns = [
        r"(?:data\s+(?:asta|vendita)|vendita\s+senza\s+incanto|asta)\s*[:\-]?\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})",
        r"(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4})",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            raw = match.group(1).replace("-", "/").replace(".", "/")
            for fmt in ("%d/%m/%Y", "%d/%m/%y"):
                try:
                    return datetime.strptime(raw, fmt).date().isoformat()
                except ValueError:
                    continue
            return raw
    return None


def extract_court(text: str) -> Optional[str]:
    match = re.search(r"tribunale\s+di\s+([A-Za-zÀ-ÿ\s']{2,60})", text, flags=re.IGNORECASE)
    if not match:
        return None
    return match.group(0).strip().title()


def extract_procedure_number(text: str) -> Optional[str]:
    patterns = [
        r"(?:procedura|r\.g\.e\.?|rge)\s*(?:n\.?|numero)?\s*[:\-]?\s*([0-9]+\s*/\s*[0-9]{2,4})",
        r"([0-9]+\s*/\s*[0-9]{2,4})\s*(?:r\.g\.e\.?|rge)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return re.sub(r"\s+", "", match.group(1))
    return None


def extract_lot_number(text: str) -> Optional[str]:
    match = re.search(r"lotto\s*(?:n\.?|numero)?\s*[:\-]?\s*([A-Za-z0-9]+)", text, flags=re.IGNORECASE)
    return match.group(1).upper() if match else None


def extract_occupation_status(text: str) -> Optional[str]:
    lowered = text.lower()
    if any(token in lowered for token in ["immobile libero", "libero da persone", "stato: libero", "occupazione: libero"]):
        return "libero"
    if any(token in lowered for token in ["occupato", "occupata", "non libero", "locato", "conduttore"]):
        return "occupato"
    return "sconosciuto"


def extract_city(text: str) -> Optional[str]:
    patterns = [
        r"comune\s+di\s+([A-Za-zÀ-ÿ\s']{2,50})",
        r"in\s+([A-Za-zÀ-ÿ\s']{2,50})\s*,\s*(?:via|viale|corso|piazza)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip(" ,.-").title()
    return None


def extract_address(text: str) -> Optional[str]:
    pattern = r"((?:via|viale|corso|piazza|strada|largo)\s+[A-Za-zÀ-ÿ0-9\s'\.]+(?:,?\s*n\.?\s*\d+|,?\s*\d+)?)"
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if not match:
        return None
    return re.sub(r"\s+", " ", match.group(1)).strip(" ,.-").title()


def detect_risk_keywords(text: str) -> List[str]:
    lowered = text.lower()
    found = []
    for keyword in RISK_KEYWORDS:
        if keyword in lowered and keyword not in found:
            found.append(keyword)
    return found


def calculate_confidence(parsed_fields: Dict[str, Any], risk_keywords: List[str]) -> str:
    present = sum(1 for field in REQUIRED_PARSED_FIELDS if parsed_fields.get(field) not in (None, ""))
    ratio = present / len(REQUIRED_PARSED_FIELDS)
    if ratio >= 0.75 and len(risk_keywords) <= 2:
        return "alta"
    if ratio >= 0.45:
        return "media"
    return "bassa"


def parse_auction_text(text: str, source_url: Optional[str] = None) -> Dict[str, Any]:
    normalized = normalize_text(text)
    parsed_fields = {
        "city": extract_city(normalized),
        "address": extract_address(normalized),
        "base_price": extract_base_price(normalized),
        "minimum_bid": extract_minimum_bid(normalized),
        "surface_sqm": extract_surface_sqm(normalized),
        "auction_date": extract_auction_date(normalized),
        "court": extract_court(normalized),
        "procedure_number": extract_procedure_number(normalized),
        "lot_number": extract_lot_number(normalized),
        "occupation_status": extract_occupation_status(normalized),
        "source_url": source_url,
    }
    missing_fields = [field for field in REQUIRED_PARSED_FIELDS if parsed_fields.get(field) in (None, "")]
    risk_keywords = detect_risk_keywords(normalized)
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
        "confidence": calculate_confidence(parsed_fields, risk_keywords),
        "notes": notes,
    }
