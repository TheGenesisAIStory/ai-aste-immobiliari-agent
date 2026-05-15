from __future__ import annotations

import json
import os
import re
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

BASE_DIR = Path(__file__).resolve().parents[3]
RAG_DIR = BASE_DIR / "data" / "processed" / "rag_index"
RAG_DIR.mkdir(parents=True, exist_ok=True)


def _index_path(document_id: int) -> Path:
    return RAG_DIR / f"document_{document_id}.json"


def chunk_text_for_rag(text: str, size: int = 900, overlap: int = 120) -> List[Dict[str, Any]]:
    normalized = re.sub(r"\s+", " ", text or "").strip()
    if not normalized:
        return []
    chunks = []
    start = 0
    while start < len(normalized):
        chunk = normalized[start : start + size].strip()
        if chunk:
            chunks.append(
                {
                    "chunk_id": uuid.uuid4().hex,
                    "page_number": None,
                    "text": chunk,
                    "metadata": {"start_char": start, "end_char": start + len(chunk)},
                }
            )
        if start + size >= len(normalized):
            break
        start += max(1, size - overlap)
    return chunks


def save_chunks(document_id: int, text: str) -> List[Dict[str, Any]]:
    chunks = chunk_text_for_rag(text)
    payload = [{"document_id": document_id, **chunk} for chunk in chunks]
    _index_path(document_id).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def get_chunks(document_id: int) -> List[Dict[str, Any]]:
    path = _index_path(document_id)
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def delete_chunks(document_id: int) -> int:
    chunks = get_chunks(document_id)
    path = _index_path(document_id)
    if path.exists():
        path.unlink()
    return len(chunks)


def _tokens(text: str) -> set[str]:
    return {token for token in re.findall(r"[A-Za-zÀ-ÿ0-9]{3,}", (text or "").lower())}


def retrieve_chunks(document_id: int, question: str, limit: int = 3) -> List[Dict[str, Any]]:
    q_tokens = _tokens(question)
    scored = []
    for chunk in get_chunks(document_id):
        c_tokens = _tokens(chunk.get("text", ""))
        score = len(q_tokens & c_tokens)
        if score:
            scored.append((score, chunk))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [chunk for _, chunk in scored[:limit]]


def _llm_available() -> bool:
    return os.getenv("LLM_ENABLED", "false").lower() == "true" and bool(os.getenv("OPENAI_API_KEY"))


def _answer_with_llm(question: str, chunks: List[Dict[str, Any]]) -> Optional[str]:
    if not _llm_available():
        return None
    context = "\n\n".join(f"[{c['chunk_id']}]\n{c['text']}" for c in chunks)
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}", "Content-Type": "application/json"},
            json={
                "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                "messages": [
                    {"role": "system", "content": "Rispondi solo usando il contesto. Se non c'e, di: Non trovato nel documento."},
                    {"role": "user", "content": f"DOMANDA: {question}\n\nCONTESTO:\n{context}"},
                ],
                "temperature": 0,
            },
            timeout=30,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception:
        return None


def answer_question(document_id: int, question: str) -> Dict[str, Any]:
    chunks = retrieve_chunks(document_id, question)
    if not chunks:
        return {
            "question": question,
            "answer": "Non trovato nel documento.",
            "confidence": "bassa",
            "citations": [],
            "mode": "keyword_rag",
        }

    llm_answer = _answer_with_llm(question, chunks)
    mode = "llm_rag" if llm_answer else "keyword_rag"
    answer = llm_answer or f"Risultati rilevanti nel documento: {chunks[0]['text'][:500]}"
    return {
        "question": question,
        "answer": answer,
        "confidence": "media",
        "citations": [
            {
                "chunk_id": chunk["chunk_id"],
                "page_number": chunk.get("page_number"),
                "text_snippet": chunk.get("text", "")[:300],
            }
            for chunk in chunks
        ],
        "mode": mode,
    }

