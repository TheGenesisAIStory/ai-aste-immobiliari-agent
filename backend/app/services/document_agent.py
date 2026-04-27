from __future__ import annotations

import re
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.services.llm_document_agent import analyze_with_llm

KEY_FIELDS = ["city", "address", "surface_sqm", "minimum_bid", "auction_date", "occupation_status"]

FIELD_NAMES = [
    "court",
    "procedure_number",
    "lot_number",
    "city",
    "zone",
    "address",
    "property_type",
    "surface_sqm",
    "commercial_surface_sqm",
    "cadastral_category",
    "floor",
    "rooms",
    "base_price",
    "minimum_bid",
    "auction_date",
    "occupation_status",
    "maintenance_status",
    "legal_risk",
    "technical_risk",
    "urban_planning_issues",
    "cadastral_irregularities",
    "building_abuses",
    "condominium_debt",
    "servitudes",
    "usufruct",
    "right_of_residence",
    "access_available",
    "photos_available",
    "expert_report_date",
]

RED_FLAG_RULES = [
    ("occupazione", "occupato senza titolo", "alta", r"occupat[oa]\s+senza\s+titolo", "verificare tempi e costi di liberazione con il custode"),
    ("occupazione", "contratto opponibile", "alta", r"contratto\s+opponibile|locazione\s+opponibile", "verificare durata e opponibilita del contratto"),
    ("occupazione", "liberazione a carico aggiudicatario", "alta", r"liberazione\s+a\s+carico\s+dell['’]?\s*aggiudicatario", "stimare costi e tempi di liberazione prima dell'offerta"),
    ("occupazione", "occupato", "media", r"\boccupat[oa]\b|non\s+libero", "chiedere conferma dello stato occupazionale aggiornato"),
    ("urbanistica/catasto", "abuso edilizio", "alta", r"abuso\s+edilizio|opere\s+abusive", "verificare sanabilita con tecnico prima dell'offerta"),
    ("urbanistica/catasto", "difformita catastale", "media", r"difformit[aà]\s+catastale", "verificare pratica catastale e costi di regolarizzazione"),
    ("urbanistica/catasto", "difformita urbanistica", "alta", r"difformit[aà]\s+urbanistica", "verificare conformita urbanistica con tecnico"),
    ("urbanistica/catasto", "sanatoria", "media", r"sanatoria|accertamento\s+di\s+conformit[aà]", "verificare se la sanatoria e possibile e gia conclusa"),
    ("urbanistica/catasto", "ordine di demolizione", "alta", r"ordine\s+di\s+demolizione|demolizione", "valutare rischio perdita valore e costi obbligatori"),
    ("diritti/vincoli", "usufrutto", "alta", r"usufrutto", "verificare titolarita e durata del diritto"),
    ("diritti/vincoli", "diritto di abitazione", "alta", r"diritto\s+di\s+abitazione", "verificare opponibilita del diritto"),
    ("diritti/vincoli", "servitu", "media", r"servit[uù]", "analizzare impatto su uso e rivendibilita"),
    ("diritti/vincoli", "vincoli paesaggistici", "media", r"vincol[oi]\s+paesaggistic[oi]", "verificare autorizzazioni per lavori futuri"),
    ("diritti/vincoli", "ipoteche non cancellabili", "alta", r"ipotec[ha].{0,80}non\s+cancellabil", "chiedere verifica notarile prima dell'offerta"),
    ("economiche", "spese condominiali arretrate", "media", r"spese\s+condominiali\s+arretrate|oneri\s+condominiali\s+arretrati", "quantificare arretrati potenzialmente a carico"),
    ("economiche", "oneri condominiali", "media", r"oneri\s+condominiali", "richiedere rendiconto condominiale aggiornato"),
    ("economiche", "lavori straordinari", "media", r"lavori\s+straordinari|manutenzione\s+straordinaria", "stimare quota lavori deliberati o probabili"),
    ("economiche", "morosita", "media", r"morosit[aà]", "verificare debiti e recuperabilita"),
    ("documentali", "perizia datata", "media", r"perizia.{0,40}(?:201[0-9]|2020|2021)", "richiedere aggiornamento informazioni prima dell'offerta"),
    ("documentali", "accesso non effettuato", "alta", r"accesso\s+non\s+effettuato|non\s+[eè]\s+stato\s+possibile\s+accedere", "considerare alta incertezza su stato interno"),
    ("documentali", "fotografie assenti", "media", r"fotografie\s+assenti|documentazione\s+fotografica\s+assente", "richiedere foto o sopralluogo"),
    ("documentali", "dati mancanti", "media", r"dati\s+mancanti|informazioni\s+non\s+disponibili", "completare manualmente le informazioni critiche"),
]


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def _parse_amount(value: str) -> Optional[float]:
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


def _first(patterns: List[str], text: str, flags: int = re.IGNORECASE) -> Optional[str]:
    for pattern in patterns:
        match = re.search(pattern, text, flags=flags)
        if match:
            return re.sub(r"\s+", " ", match.group(1)).strip(" ,.;:-")
    return None


def _first_amount(patterns: List[str], text: str) -> Optional[float]:
    value = _first(patterns, text)
    return _parse_amount(value or "")


def _date(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    raw = value.replace("-", "/").replace(".", "/")
    for fmt in ("%d/%m/%Y", "%d/%m/%y"):
        try:
            return datetime.strptime(raw, fmt).date().isoformat()
        except ValueError:
            continue
    return value


def _snippet(text: str, pattern: str) -> Optional[str]:
    match = re.search(rf"(.{{0,120}}{pattern}.{{0,120}})", text, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", match.group(1)).strip() if match else None


def extract_fields(text: str) -> Dict[str, Any]:
    normalized = normalize_text(text)
    lowered = normalized.lower()

    fields = {name: None for name in FIELD_NAMES}
    fields.update(
        {
            "court": _first([r"(tribunale\s+di\s+[A-Za-zÀ-ÿ\s']{2,60})"], normalized),
            "procedure_number": _first([r"(?:procedura|r\.g\.e\.?|rge)\s*(?:n\.?|numero)?\s*[:\-]?\s*([0-9]+\s*/\s*[0-9]{2,4})"], normalized),
            "lot_number": _first([r"lotto\s*(?:n\.?|numero)?\s*[:\-]?\s*([A-Za-z0-9]+)"], normalized),
            "city": _first([r"comune\s+di\s+([A-Za-zÀ-ÿ\s']{2,50})", r"immobile\s+sito\s+in\s+([A-Za-zÀ-ÿ\s']{2,50})"], normalized),
            "zone": _first([r"zona\s+([A-Za-zÀ-ÿ0-9\s']{2,50})"], normalized),
            "address": _first([r"((?:via|viale|corso|piazza|strada|largo)\s+[A-Za-zÀ-ÿ0-9\s'\.]+(?:,?\s*n\.?\s*\d+|,?\s*\d+)?)"], normalized),
            "property_type": _first([r"(appartamento|villa|box|garage|magazzino|negozio|ufficio|terreno|fabbricato)"], lowered),
            "surface_sqm": _first_amount([r"(?:superficie|consistenza)\s*(?:commerciale)?\s*[:\-]?\s*([0-9]+(?:[\.,][0-9]+)?)\s*(?:mq|m²|metri)", r"([0-9]+(?:[\.,][0-9]+)?)\s*(?:mq|m²)\s*(?:commerciali|circa)"], normalized),
            "commercial_surface_sqm": _first_amount([r"superficie\s+commerciale\s*[:\-]?\s*([0-9]+(?:[\.,][0-9]+)?)\s*(?:mq|m²)"], normalized),
            "cadastral_category": _first([r"categoria\s+catastale\s*[:\-]?\s*([A-Z]\/?[0-9]+)"], normalized),
            "floor": _first([r"piano\s*[:\-]?\s*([A-Za-z0-9]+)"], normalized),
            "rooms": _first_amount([r"(?:vani|locali)\s*[:\-]?\s*([0-9]+(?:[\.,][0-9]+)?)"], normalized),
            "base_price": _first_amount([r"prezzo\s+base(?:\s+d['’]asta)?\s*(?:euro|€|eur)?\s*[:\-]?\s*([0-9\.\,]+)"], normalized),
            "minimum_bid": _first_amount([r"offerta\s+minima\s*(?:euro|€|eur)?\s*[:\-]?\s*([0-9\.\,]+)"], normalized),
            "auction_date": _date(_first([r"(?:data\s+(?:asta|vendita)|asta)\s*[:\-]?\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})"], normalized)),
            "expert_report_date": _date(_first([r"(?:perizia|relazione)\s+(?:del|datata)\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})"], normalized)),
        }
    )

    if re.search(r"immobile\s+libero|libero\s+da\s+persone|occupazione\s*[:\-]?\s*libero", lowered):
        fields["occupation_status"] = "libero"
    elif re.search(r"occupat[oa]|non\s+libero|locato", lowered):
        fields["occupation_status"] = "occupato"
    else:
        fields["occupation_status"] = "sconosciuto"

    fields["maintenance_status"] = _first([r"stato\s+manutentivo\s*[:\-]?\s*([A-Za-zÀ-ÿ\s']{2,60})"], normalized)
    fields["urban_planning_issues"] = bool(re.search(r"difformit[aà]\s+urbanistica|abuso|sanatoria|demolizione", lowered))
    fields["cadastral_irregularities"] = bool(re.search(r"difformit[aà]\s+catastale|catastalmente\s+non\s+conforme", lowered))
    fields["building_abuses"] = bool(re.search(r"abuso\s+edilizio|opere\s+abusive", lowered))
    fields["condominium_debt"] = bool(re.search(r"spese\s+condominiali\s+arretrate|morosit[aà]|oneri\s+condominiali", lowered))
    fields["servitudes"] = bool(re.search(r"servit[uù]", lowered))
    fields["usufruct"] = bool(re.search(r"usufrutto", lowered))
    fields["right_of_residence"] = bool(re.search(r"diritto\s+di\s+abitazione", lowered))
    fields["access_available"] = False if re.search(r"accesso\s+non\s+effettuato|non\s+[eè]\s+stato\s+possibile\s+accedere", lowered) else None
    fields["photos_available"] = False if re.search(r"fotografie\s+assenti|documentazione\s+fotografica\s+assente", lowered) else None

    legal_flags = [fields["servitudes"], fields["usufruct"], fields["right_of_residence"]]
    technical_flags = [fields["urban_planning_issues"], fields["cadastral_irregularities"], fields["building_abuses"]]
    fields["legal_risk"] = "alto" if any(legal_flags) else "medio"
    fields["technical_risk"] = "alto" if any(technical_flags) else "medio"
    return fields


def detect_red_flags(text: str) -> List[Dict[str, str]]:
    normalized = normalize_text(text)
    flags = []
    seen = set()
    for category, label, severity, pattern, action in RED_FLAG_RULES:
        evidence = _snippet(normalized, pattern)
        key = (category, label)
        if evidence and key not in seen:
            seen.add(key)
            flags.append(
                {
                    "category": category,
                    "label": label,
                    "severity": severity,
                    "evidence": evidence[:260],
                    "suggested_action": action,
                }
            )
    return flags


def _confidence(fields: Dict[str, Any], red_flags: List[Dict[str, str]], text: str) -> str:
    if len(normalize_text(text)) < 100:
        return "bassa"
    present = sum(1 for field in KEY_FIELDS if fields.get(field) not in (None, "", "sconosciuto"))
    if present >= 5 and len(red_flags) <= 2:
        return "alta"
    if present >= 3:
        return "media"
    return "bassa"


def _summary(fields: Dict[str, Any], red_flags: List[Dict[str, str]], missing: List[str]) -> str:
    parts = []
    location = fields.get("address") or fields.get("city")
    if location:
        parts.append(f"Immobile sito in {location}")
    if fields.get("surface_sqm"):
        parts.append(f"superficie {fields['surface_sqm']} mq")
    if fields.get("minimum_bid"):
        parts.append(f"offerta minima {fields['minimum_bid']}")
    if fields.get("occupation_status"):
        parts.append(f"stato occupazione {fields['occupation_status']}")

    if not parts:
        base = "Documento analizzato, ma i campi principali non sono stati estratti."
    else:
        base = ", ".join(parts) + "."

    risk_labels = [flag["label"] for flag in red_flags[:5]]
    risks = " Rischi principali: " + ", ".join(risk_labels) + "." if risk_labels else " Rischi principali: non emersi dalle regole MVP."
    missing_text = " Campi da verificare manualmente: " + ", ".join(missing) + "." if missing else " Campi chiave principali presenti."
    return base + risks + missing_text


def _sections(text: str) -> Dict[str, Optional[str]]:
    return {
        "occupazione": _snippet(text, r"occupat[oa]|libero|locato"),
        "urbanistica": _snippet(text, r"abuso|difformit[aà]|sanatoria|demolizione"),
        "vincoli": _snippet(text, r"ipoteca|usufrutto|servit[uù]|diritto\s+di\s+abitazione"),
    }


def _valuation_draft(fields: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "city": fields.get("city"),
        "zone": fields.get("zone"),
        "address": fields.get("address"),
        "minimum_bid": fields.get("minimum_bid"),
        "surface_sqm": fields.get("commercial_surface_sqm") or fields.get("surface_sqm"),
        "occupation_status": fields.get("occupation_status"),
        "legal_risk": fields.get("legal_risk"),
        "technical_risk": fields.get("technical_risk"),
    }


def _field_evidence(text: str, value: Any) -> str:
    if value in (None, "", False):
        return ""
    if isinstance(value, bool):
        return ""
    snippet = _snippet(text, re.escape(str(value)))
    return snippet or str(value)[:160]


def fields_with_metadata(fields: Dict[str, Any], text: str, source: str = "rule_based") -> Dict[str, Dict[str, Any]]:
    result = {}
    for key, value in fields.items():
        present = value not in (None, "", "sconosciuto")
        result[key] = {
            "value": value,
            "confidence": "media" if present else "bassa",
            "evidence": _field_evidence(text, value),
            "source": source,
        }
    return result


def analyze_document(
    text: str,
    document_id: Optional[str] = None,
    filename: Optional[str] = None,
    ocr_metadata: Optional[Dict[str, Any]] = None,
    use_llm: bool = True,
) -> Dict[str, Any]:
    normalized = normalize_text(text)
    fields = extract_fields(normalized)
    red_flags = detect_red_flags(normalized)
    missing = [field for field in KEY_FIELDS if fields.get(field) in (None, "", "sconosciuto")]
    confidence = _confidence(fields, red_flags, normalized)
    risk_level = "basso"
    if any(flag["severity"] == "alta" for flag in red_flags) or len(red_flags) >= 4:
        risk_level = "alto"
    elif red_flags:
        risk_level = "medio"

    notes = ["Analisi rule-based: non inventa valori mancanti."]
    if not normalized:
        notes.append("Testo vuoto o non leggibile: possibile PDF scansito senza OCR.")

    llm_output = analyze_with_llm(normalized) if use_llm else None
    analysis_mode = "rule_based"
    field_payload = fields_with_metadata(fields, normalized)
    if llm_output is not None:
        analysis_mode = "hybrid"
        for key, value in llm_output.fields.items():
            field_payload[key] = value.dict()
        if llm_output.red_flags:
            red_flags = [flag.dict() for flag in llm_output.red_flags]
        if llm_output.missing_fields:
            missing = llm_output.missing_fields
        if llm_output.summary:
            summary = llm_output.summary
        else:
            summary = _summary(fields, red_flags, missing)
        confidence = llm_output.confidence or confidence
    else:
        summary = _summary(fields, red_flags, missing)

    ocr_metadata = ocr_metadata or {}
    return {
        "document_id": document_id or uuid.uuid4().hex,
        "filename": filename,
        "analysis_mode": analysis_mode,
        "fields": field_payload,
        "summary": summary,
        "extracted_fields": fields,
        "sections": _sections(normalized),
        "red_flags": red_flags,
        "missing_fields": missing,
        "risk_level": risk_level,
        "confidence": confidence,
        "ocr_used": bool(ocr_metadata.get("ocr_used", False)),
        "ocr_pages": ocr_metadata.get("ocr_pages", []),
        "text_extraction_method": ocr_metadata.get("text_extraction_method", "native"),
        "warnings": ocr_metadata.get("warnings", []),
        "rag_available": False,
        "valuation_draft": _valuation_draft(fields),
        "notes": notes,
    }
