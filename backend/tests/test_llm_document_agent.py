from __future__ import annotations


def test_llm_disabled_uses_rule_based(monkeypatch) -> None:
    from app.services.document_agent import analyze_document

    monkeypatch.setenv("LLM_ENABLED", "false")
    analysis = analyze_document("Comune di Torino, Via Roma 10. Offerta minima euro 90.000.")

    assert analysis["analysis_mode"] == "rule_based"
    assert analysis["fields"]["city"]["source"] == "rule_based"


def test_llm_error_falls_back_to_rule_based(monkeypatch) -> None:
    from app.services import llm_document_agent
    from app.services.document_agent import analyze_document

    monkeypatch.setenv("LLM_ENABLED", "true")
    monkeypatch.setenv("OPENAI_API_KEY", "test")
    monkeypatch.setattr(llm_document_agent.requests, "post", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("boom")))

    analysis = analyze_document("Comune di Torino, Via Roma 10. Offerta minima euro 90.000.")

    assert analysis["analysis_mode"] == "rule_based"
    assert analysis["fields"]["minimum_bid"]["value"] == 90000


def test_llm_output_schema_validates() -> None:
    from app.services.llm_document_agent import LLMDocumentOutput

    payload = {
        "fields": {"city": {"value": "Torino", "confidence": "alta", "evidence": "Comune di Torino", "source": "llm"}},
        "red_flags": [],
        "summary": "Immobile in Torino.",
        "missing_fields": [],
        "confidence": "alta",
    }
    parsed = LLMDocumentOutput(**payload)
    assert parsed.fields["city"].value == "Torino"

