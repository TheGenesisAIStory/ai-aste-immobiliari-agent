from __future__ import annotations

from app.services.document_agent import analyze_document


def test_document_agent_detects_structured_red_flags() -> None:
    text = """
    Tribunale di Torino. Comune di Torino, Via Roma 10. Superficie 80 mq.
    Offerta minima euro 90.000. Data asta 30/05/2026.
    Immobile occupato senza titolo. Presente difformità catastale e abuso edilizio.
    Spese condominiali arretrate. Accesso non effettuato.
    """
    analysis = analyze_document(text)

    labels = {flag["label"] for flag in analysis["red_flags"]}
    assert "occupato senza titolo" in labels
    assert "difformita catastale" in labels
    assert analysis["confidence"] in {"media", "alta"}
    assert analysis["summary"]
    assert analysis["valuation_draft"]["minimum_bid"] == 90000


def test_document_agent_low_confidence_for_poor_text() -> None:
    analysis = analyze_document("pdf non leggibile")
    assert analysis["confidence"] == "bassa"
    assert "city" in analysis["missing_fields"]
