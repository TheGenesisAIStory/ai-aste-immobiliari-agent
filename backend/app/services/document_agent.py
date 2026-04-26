from __future__ import annotations

import re
from typing import Optional

RED_FLAG_KEYWORDS = [
    "abuso",
    "difformità",
    "occupato",
    "ipoteca",
    "pignoramento",
    "servitù",
    "usufrutto",
]


def analyze_document(text: str) -> dict:
    lowered = text.lower()

    red_flags = [k for k in RED_FLAG_KEYWORDS if k in lowered]

    sections = {
        "occupazione": _extract_section(lowered, "occupato"),
        "urbanistica": _extract_section(lowered, "abuso"),
        "vincoli": _extract_section(lowered, "ipoteca"),
    }

    risk_level = "basso"
    if len(red_flags) >= 3:
        risk_level = "alto"
    elif len(red_flags) >= 1:
        risk_level = "medio"

    return {
        "red_flags": red_flags,
        "sections": sections,
        "risk_level": risk_level,
        "confidence": "media" if text else "bassa",
        "notes": ["Analisi rule-based (no AI LLM)"]
    }


def _extract_section(text: str, keyword: str) -> Optional[str]:
    match = re.search(rf"(.{{0,100}}{keyword}.{{0,100}})", text)
    return match.group(0) if match else None
