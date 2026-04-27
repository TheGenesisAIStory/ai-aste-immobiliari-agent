from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

import requests
from pydantic import BaseModel, Field, ValidationError


class FieldExtraction(BaseModel):
    value: Any = None
    confidence: str = "bassa"
    evidence: str = ""
    source: str = "llm"


class LLMRedFlag(BaseModel):
    category: str
    label: str
    severity: str
    evidence: str
    suggested_action: str


class LLMDocumentOutput(BaseModel):
    fields: Dict[str, FieldExtraction] = Field(default_factory=dict)
    red_flags: list[LLMRedFlag] = Field(default_factory=list)
    summary: str = ""
    missing_fields: list[str] = Field(default_factory=list)
    confidence: str = "bassa"


def llm_enabled() -> bool:
    return os.getenv("LLM_ENABLED", "false").lower() == "true" and bool(os.getenv("OPENAI_API_KEY"))


def _max_chars() -> int:
    try:
        return int(os.getenv("LLM_MAX_CHARS", "60000"))
    except ValueError:
        return 60000


def _prompt(text: str) -> str:
    return (
        "Sei un assistente per analisi di perizie immobiliari italiane. "
        "Estrai solo dati presenti nel documento. Non stimare valori economici, non inventare campi. "
        "Ogni campo deve avere value, confidence, evidence breve e source='llm'. "
        "Classifica rischi con severity bassa/media/alta. Restituisci solo JSON valido.\n\n"
        f"DOCUMENTO:\n{text[:_max_chars()]}"
    )


def _call_openai(text: str) -> Dict[str, Any]:
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": model,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": "Rispondi solo con JSON validabile."},
                {"role": "user", "content": _prompt(text)},
            ],
            "temperature": 0,
        },
        timeout=60,
    )
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"]
    return json.loads(content)


def analyze_with_llm(text: str) -> Optional[LLMDocumentOutput]:
    if not llm_enabled():
        return None
    try:
        return LLMDocumentOutput(**_call_openai(text))
    except Exception:
        return None
