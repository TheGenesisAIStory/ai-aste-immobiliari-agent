from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional, Tuple

import pandas as pd
import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")

st.set_page_config(page_title="AI Aste Immobiliari", layout="wide")
st.title("AI Aste Immobiliari")
st.caption(f"Backend: {BACKEND_URL}")


def request_json(method: str, path: str, payload: Optional[dict] = None) -> Tuple[Optional[Any], Optional[str]]:
    try:
        response = requests.request(method, f"{BACKEND_URL}{path}", json=payload, timeout=25)
        response.raise_for_status()
        return response.json(), None
    except requests.RequestException as exc:
        detail = getattr(exc.response, "text", "") if getattr(exc, "response", None) is not None else ""
        return None, f"Errore backend: {exc}. {detail}"


def post_file(path: str, field: str, uploaded_file, data: Optional[dict] = None) -> Tuple[Optional[dict], Optional[str]]:
    try:
        files = {field: (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
        response = requests.post(f"{BACKEND_URL}{path}", files=files, data=data, timeout=60)
        response.raise_for_status()
        return response.json(), None
    except requests.RequestException as exc:
        detail = getattr(exc.response, "text", "") if getattr(exc, "response", None) is not None else ""
        return None, f"Errore backend: {exc}. {detail}"


def show_error(error: Optional[str]) -> bool:
    if error:
        st.warning(error)
        return True
    return False


def valuation_form(prefix: str, defaults: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    defaults = defaults or {}
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        city = st.text_input("Citta", defaults.get("city") or "Torino", key=f"{prefix}_city")
        zone = st.text_input("Zona", defaults.get("zone") or "", key=f"{prefix}_zone")
        address = st.text_input("Indirizzo", defaults.get("address") or "", key=f"{prefix}_address")
        minimum_bid = st.number_input("Offerta minima", min_value=1.0, value=float(defaults.get("minimum_bid") or 90000), key=f"{prefix}_bid")
    with col_b:
        surface_sqm = st.number_input("Superficie mq", min_value=1.0, value=float(defaults.get("surface_sqm") or 80), key=f"{prefix}_surface")
        market_price = st.number_input("Prezzo mercato €/mq", min_value=1.0, value=float(defaults.get("estimated_market_price_per_sqm") or 2500), key=f"{prefix}_market")
        renovation_cost = st.number_input("Costi ristrutturazione", min_value=0.0, value=float(defaults.get("renovation_cost") or 0), key=f"{prefix}_renovation")
        other_costs = st.number_input("Altri costi", min_value=0.0, value=float(defaults.get("other_costs") or 0), key=f"{prefix}_other")
    with col_c:
        rent = st.number_input("Affitto mensile atteso", min_value=0.0, value=float(defaults.get("expected_monthly_rent") or 0), key=f"{prefix}_rent")
        occupation = st.selectbox("Occupazione", ["libero", "occupato", "sconosciuto"], index=["libero", "occupato", "sconosciuto"].index(defaults.get("occupation_status") or "libero"), key=f"{prefix}_occupation")
        legal_risk = st.selectbox("Rischio legale", ["basso", "medio", "alto"], index=["basso", "medio", "alto"].index(defaults.get("legal_risk") or "medio"), key=f"{prefix}_legal")
        technical_risk = st.selectbox("Rischio tecnico", ["basso", "medio", "alto"], index=["basso", "medio", "alto"].index(defaults.get("technical_risk") or "medio"), key=f"{prefix}_technical")

    return {
        "city": city,
        "zone": zone or None,
        "address": address or None,
        "minimum_bid": minimum_bid,
        "surface_sqm": surface_sqm,
        "estimated_market_price_per_sqm": market_price,
        "renovation_cost": renovation_cost,
        "other_costs": other_costs,
        "expected_monthly_rent": rent,
        "occupation_status": occupation,
        "legal_risk": legal_risk,
        "technical_risk": technical_risk,
    }


def show_valuation_metrics(result: Dict[str, Any]) -> None:
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("Valore mercato", f"€ {result.get('estimated_market_value', result.get('market_value_estimate', 0)):,.0f}")
    col2.metric("Costo totale", f"€ {result.get('total_investment', result.get('total_cost', 0)):,.0f}")
    col3.metric("Margine", f"€ {result.get('gross_margin', 0):,.0f}")
    col4.metric("ROI", f"{result.get('gross_roi_percent', result.get('gross_roi', 0)):.1f}%")
    col5.metric("Affitto", f"{result.get('gross_yield_percent', result.get('rental_yield', 0)):.1f}%")
    col6.metric("Score", f"{result.get('score', 0):.1f}")
    st.info(f"Raccomandazione: {result.get('recommendation', '-')}")


def save_valuation_from_payload(payload: Dict[str, Any]) -> None:
    result, error = request_json("POST", "/valuations", payload)
    if not show_error(error) and result:
        st.success(f"Valutazione salvata con ID {result['id']}")
        show_valuation_metrics(result)
        with st.expander("Record salvato"):
            st.json(result)


tabs = st.tabs([
    "Valuta asta",
    "Storico valutazioni",
    "Import URL/PDF",
    "Analisi perizia avanzata",
    "Q&A documento",
    "Documenti analizzati",
    "Info progetto",
])

with tabs[0]:
    payload = valuation_form("preview")
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Preview valutazione", type="primary"):
            result, error = request_json("POST", "/valuate", payload)
            if not show_error(error) and result:
                show_valuation_metrics(result)
                with st.expander("JSON preview"):
                    st.json(result)
    with col_b:
        if st.button("Salva valutazione"):
            save_valuation_from_payload(payload)

with tabs[1]:
    data, error = request_json("GET", "/valuations")
    if show_error(error):
        data = []
    if not data:
        st.info("Nessuna valutazione salvata.")
    else:
        df = pd.DataFrame(data)
        city = st.selectbox("Citta", ["Tutte"] + sorted([c for c in df["city"].dropna().unique()]))
        recommendation = st.selectbox("Raccomandazione", ["Tutte"] + sorted([r for r in df["recommendation"].dropna().unique()]))
        score_min = st.slider("Score minimo", 0.0, 100.0, 0.0)
        sort_by = st.selectbox("Ordina per", ["created_at", "score"])
        filtered = df.copy()
        if city != "Tutte":
            filtered = filtered[filtered["city"] == city]
        if recommendation != "Tutte":
            filtered = filtered[filtered["recommendation"] == recommendation]
        filtered = filtered[filtered["score"] >= score_min].sort_values(sort_by, ascending=False)
        st.dataframe(filtered, use_container_width=True)
        st.download_button("Export CSV", filtered.to_csv(index=False).encode("utf-8"), "valuations.csv", "text/csv")
        selected_id = st.number_input("ID dettaglio/elimina", min_value=1, step=1)
        if st.button("Mostra dettaglio valutazione"):
            detail, detail_error = request_json("GET", f"/valuations/{selected_id}")
            if not show_error(detail_error) and detail:
                st.json(detail)
        if st.button("Elimina valutazione"):
            deleted, delete_error = request_json("DELETE", f"/valuations/{selected_id}")
            if not show_error(delete_error):
                st.success(f"Valutazione {selected_id} eliminata.")

with tabs[2]:
    import_mode = st.radio("Tipo import", ["URL", "PDF"], horizontal=True)
    imported = None
    if import_mode == "URL":
        source_url = st.text_input("URL asta")
        if st.button("Importa URL") and source_url:
            imported, error = request_json("POST", "/imports/url", {"source_url": source_url})
            show_error(error)
    else:
        pdf = st.file_uploader("PDF asta", type=["pdf"], key="import_pdf")
        if st.button("Importa PDF") and pdf:
            imported, error = post_file("/imports/pdf", "file", pdf)
            show_error(error)
    if imported:
        st.subheader("Preview import")
        st.text_area("Testo estratto", imported.get("extracted_text_preview", ""), height=140)
        st.json({
            "parsed_fields": imported.get("parsed_fields"),
            "missing_fields": imported.get("missing_fields"),
            "risk_keywords": imported.get("risk_keywords"),
            "confidence": imported.get("confidence"),
        })
        draft = imported.get("parsed_fields") or {}
        st.subheader("Bozza valutazione")
        completed = valuation_form("import_draft", draft)
        if st.button("Salva valutazione da import"):
            save_valuation_from_payload(completed)

with tabs[3]:
    perizia = st.file_uploader("PDF perizia", type=["pdf"], key="document_pdf")
    use_llm = st.checkbox("Usa LLM se disponibile", value=False)
    analysis = None
    if st.button("Analizza perizia") and perizia:
        analysis, error = post_file("/documents/upload", "file", perizia, data={"use_llm": str(use_llm).lower()})
        show_error(error)
    if analysis:
        st.subheader("Sintesi")
        st.write(analysis.get("summary"))
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Confidence", analysis.get("confidence", "-"))
        c2.metric("Modalita", analysis.get("analysis_mode", "-"))
        c3.metric("OCR usato", "si" if analysis.get("ocr_used") else "no")
        c4.metric("Metodo testo", analysis.get("text_extraction_method", "-"))
        if analysis.get("ocr_pages"):
            st.caption(f"Pagine OCR: {analysis.get('ocr_pages')}")
        if analysis.get("warnings"):
            st.warning(" | ".join(analysis.get("warnings")))
        st.subheader("Campi con evidence")
        st.dataframe(pd.DataFrame.from_dict(analysis.get("fields") or {}, orient="index"), use_container_width=True)
        st.subheader("Red flags")
        st.dataframe(pd.DataFrame(analysis.get("red_flags") or []), use_container_width=True)
        st.json({
            "extracted_fields": analysis.get("extracted_fields"),
            "missing_fields": analysis.get("missing_fields"),
            "rag_available": analysis.get("rag_available"),
        })
        st.subheader("Bozza valutazione")
        draft = analysis.get("valuation_draft") or {}
        completed = valuation_form("document_draft", draft)
        if st.button("Salva valutazione da perizia"):
            save_valuation_from_payload(completed)

with tabs[4]:
    docs, error = request_json("GET", "/documents")
    if show_error(error):
        docs = []
    if not docs:
        st.info("Nessun documento disponibile per Q&A.")
    else:
        options = {f"{doc['id']} - {doc['filename']}": doc["id"] for doc in docs}
        selected = st.selectbox("Documento", list(options.keys()))
        question = st.text_input("Domanda sul documento", "L'immobile è occupato?")
        if st.button("Chiedi al documento"):
            answer, ask_error = request_json("POST", f"/documents/{options[selected]}/ask", {"question": question})
            if not show_error(ask_error) and answer:
                st.metric("Modalita", answer.get("mode", "-"))
                st.write(answer.get("answer"))
                with st.expander("Citazioni"):
                    st.json(answer.get("citations"))
        if st.button("Mostra chunks"):
            chunks, chunk_error = request_json("GET", f"/documents/{options[selected]}/chunks")
            if not show_error(chunk_error):
                st.dataframe(pd.DataFrame(chunks), use_container_width=True)
        if st.button("Reindicizza documento"):
            reindexed, reindex_error = request_json("POST", f"/documents/{options[selected]}/reindex")
            if not show_error(reindex_error):
                st.success(f"Chunks creati: {reindexed.get('chunks', 0)}")

with tabs[5]:
    docs, error = request_json("GET", "/documents")
    if show_error(error):
        docs = []
    if not docs:
        st.info("Nessun documento analizzato.")
    else:
        docs_df = pd.DataFrame(docs)
        st.dataframe(docs_df[["id", "filename", "page_count", "confidence", "created_at"]], use_container_width=True)
        doc_id = st.number_input("ID documento", min_value=1, step=1, key="doc_id")
        if st.button("Mostra dettaglio documento"):
            detail, detail_error = request_json("GET", f"/documents/{doc_id}")
            if not show_error(detail_error) and detail:
                st.json(detail)
                st.download_button("Export JSON", json.dumps(detail, indent=2, ensure_ascii=False), f"document_{doc_id}.json", "application/json")
        if st.button("Elimina documento"):
            deleted, delete_error = request_json("DELETE", f"/documents/{doc_id}")
            if not show_error(delete_error):
                st.success(
                    f"Documento {doc_id} eliminato. "
                    f"File: {deleted.get('deleted_file')}; chunks: {deleted.get('deleted_chunks')}"
                )

with tabs[6]:
    st.markdown(
        """
        MVP per valutazione aste immobiliari con backend FastAPI, SQLite/PostgreSQL via SQLAlchemy,
        import URL/PDF, OCR opzionale, LLM opzionale, RAG locale e dashboard Streamlit con storico persistente.

        Endpoint principali:
        `/health`, `/valuate`, `/valuations`, `/imports/url`, `/imports/pdf`, `/imports`,
        `/documents/upload`, `/documents`, `/documents/{id}/ask`, `/documents/{id}/chunks`.

        Limiti noti:
        l'import URL scarica una sola pagina, non fa crawling; OCR richiede Tesseract installato;
        LLM e embeddings sono opzionali;
        le stime non sostituiscono verifiche professionali.

        Disclaimer:
        questo strumento non costituisce consulenza finanziaria, legale, fiscale o immobiliare.
        """
    )
