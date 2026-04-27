from __future__ import annotations


def test_chunking_and_keyword_retrieval(tmp_path, monkeypatch) -> None:
    from app.services import rag_service

    monkeypatch.setattr(rag_service, "RAG_DIR", tmp_path)
    chunks = rag_service.save_chunks(1, "L'immobile risulta occupato. Sono presenti abusi edilizi.")

    assert chunks
    retrieved = rag_service.retrieve_chunks(1, "immobile occupato")
    assert retrieved
    assert "occupato" in retrieved[0]["text"]


def test_ask_without_llm_and_delete_chunks(tmp_path, monkeypatch) -> None:
    from app.services import rag_service

    monkeypatch.setattr(rag_service, "RAG_DIR", tmp_path)
    monkeypatch.setenv("LLM_ENABLED", "false")
    rag_service.save_chunks(2, "Offerta minima euro 90.000. Immobile libero.")

    answer = rag_service.answer_question(2, "Qual è offerta minima?")

    assert answer["mode"] == "keyword_rag"
    assert answer["citations"]
    assert rag_service.delete_chunks(2) > 0
    assert rag_service.get_chunks(2) == []

