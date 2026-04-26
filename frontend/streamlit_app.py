from __future__ import annotations

import os

import pandas as pd
import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")

st.set_page_config(page_title="AI Aste Immobiliari", layout="wide")
st.title("AI Aste Immobiliari")


def post_json(path: str, payload: dict) -> tuple[dict | None, str | None]:
    try:
        response = requests.post(f"{BACKEND_URL}{path}", json=payload, timeout=20)
        response.raise_for_status()
        return response.json(), None
    except requests.RequestException as exc:
        return None, f"Backend non raggiungibile o errore API: {exc}"


def post_file(path: str, field: str, uploaded_file) -> tuple[dict | None, str | None]:
    try:
        files = {field: (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
        response = requests.post(f"{BACKEND_URL}{path}", files=files, timeout=40)
        response.raise_for_status()
        return response.json(), None
    except requests.RequestException as exc:
        return None, f"Backend non raggiungibile o errore API: {exc}"


tabs = st.tabs(["Valutazione", "Import URL", "Import PDF", "Documenti"])

with tabs[0]:
    col_a, col_b = st.columns(2)
    with col_a:
        city = st.text_input("Citta", "Torino")
        zone = st.text_input("Zona", "San Donato")
        address = st.text_input("Indirizzo", "Via esempio 10")
        minimum_bid = st.number_input("Offerta minima", min_value=1.0, value=90000.0)
        surface_sqm = st.number_input("Superficie mq", min_value=1.0, value=80.0)
        market_price = st.number_input("Prezzo mercato €/mq", min_value=1.0, value=2500.0)
    with col_b:
        renovation_cost = st.number_input("Costi ristrutturazione", min_value=0.0, value=25000.0)
        other_costs = st.number_input("Altri costi", min_value=0.0, value=8000.0)
        rent = st.number_input("Affitto mensile atteso", min_value=0.0, value=850.0)
        occupation = st.selectbox("Occupazione", ["libero", "occupato", "sconosciuto"])
        legal_risk = st.selectbox("Rischio legale", ["basso", "medio", "alto"])
        technical_risk = st.selectbox("Rischio tecnico", ["basso", "medio", "alto"])

    if st.button("Valuta asta", type="primary"):
        result, error = post_json(
            "/valuate",
            {
                "city": city,
                "zone": zone,
                "address": address,
                "minimum_bid": minimum_bid,
                "surface_sqm": surface_sqm,
                "estimated_market_price_per_sqm": market_price,
                "renovation_cost": renovation_cost,
                "other_costs": other_costs,
                "expected_monthly_rent": rent,
                "occupation_status": occupation,
                "legal_risk": legal_risk,
                "technical_risk": technical_risk,
            },
        )
        if error:
            st.warning(error)
        elif result:
            metrics = pd.DataFrame([result])
            st.dataframe(metrics, use_container_width=True)

with tabs[1]:
    source_url = st.text_input("URL annuncio o pagina asta")
    if st.button("Importa URL") and source_url:
        result, error = post_json("/imports/url", {"source_url": source_url})
        st.warning(error) if error else st.json(result)

with tabs[2]:
    pdf = st.file_uploader("PDF asta", type=["pdf"], key="import_pdf")
    if st.button("Importa PDF") and pdf:
        result, error = post_file("/imports/pdf", "file", pdf)
        st.warning(error) if error else st.json(result)

with tabs[3]:
    document = st.file_uploader("Perizia o documento PDF", type=["pdf"], key="document_pdf")
    if st.button("Analizza documento") and document:
        result, error = post_file("/documents/upload", "file", document)
        st.warning(error) if error else st.json(result)
