#!/usr/bin/env python3
"""
Script 03 — Genera report finale con solo i migliori immobili e prompt LLM pronto.
Input:  data/output/immobili_scored.csv
Output: data/output/report_finale.csv
         data/output/prompts_llm/prompt_{i}.txt  (uno per immobile da approfondire)
"""
import os
import pandas as pd
from utils import get_logger, ROOT, load_config

logger = get_logger("03_genera_report")
config = load_config()

PROMPT_TEMPLATE = """
Agisci come analista immobiliare senior per {city}.

Analizza questa proprietà:

- Città: {city}
- Zona: {zona}
- Link: {link}
- Prezzo richiesto: {prezzo} €
- Prezzo €/mq: {prezzo_mq} €/mq
- Mq: {mq}
- Offerta minima asta: {offerta_minima}
- All'asta: {astato}
- Occupato: {occupato}
- Piano: {piano}
- Ascensore: {ascensore}
- Spese condominiali: {spese} €/mese
- Classe energetica: {classe_energetica}
- Comparabile avg zona: {comparabile_avg} €/mq
- Sconto stimato: {discount:.0%}
- Link perizia: {link_perizia}
- Note: {note}

Task:
1. Valuta se il prezzo €/mq è coerente con la zona.
2. Se è un'asta, analizza:
   - se lo sconto è reale o solo apparente;
   - rischi di occupazione, abusi, costi straordinari;
   - costo totale stimato all-in.
3. Assegna score 0–100 su:
   - posizione
   - qualità immobile
   - convenienza economica
   - rischio complessivo
4. Dai un range di valore plausibile.
5. Dai un range di offerta consigliata (aggressiva / realistica / massima).
6. Verdetto finale: scarta / monitora / approfondisci / fai offerta.

Non inventare dati mancanti. Se mancano, elencali.

Output:
- Sintesi (3-4 righe)
- Red flag
- Valore stimato min / max
- Offerta aggressiva / realistica / massima
- Verdetto finale
"""


def main():
    in_path = os.path.join(ROOT, "data", "output", "immobili_scored.csv")
    if not os.path.exists(in_path):
        logger.error(f"File non trovato: {in_path} — esegui prima 02_calcola_score.py")
        return
    df = pd.read_csv(in_path, encoding="utf-8")
    # Filtra solo approfondisci / offerta
    interessanti = df[df["score_finale"] >= config["verdetti"]["approfondisci"]].copy()
    interessanti = interessanti.sort_values("score_finale", ascending=False)
    # Salva report CSV
    out_csv = os.path.join(ROOT, "data", "output", "report_finale.csv")
    interessanti.to_csv(out_csv, index=False, encoding="utf-8")
    logger.info(f"✅ Report finale: {len(interessanti)} immobili interessanti → {out_csv}")
    # Genera prompt LLM per ognuno
    prompts_dir = os.path.join(ROOT, "data", "output", "prompts_llm")
    os.makedirs(prompts_dir, exist_ok=True)
    for i, row in interessanti.iterrows():
        data = row.to_dict()
        # Valori di default se mancanti
        data.setdefault("offerta_minima", "N/D")
        data.setdefault("link_perizia", "N/D")
        data.setdefault("note", "")
        data.setdefault("comparabile_avg", "N/D")
        discount_val = data.get("discount", 0)
        try:
            data["discount"] = float(discount_val) if discount_val and str(discount_val) != "nan" else 0.0
        except (ValueError, TypeError):
            data["discount"] = 0.0
        prompt = PROMPT_TEMPLATE.format(**{k: v if v is not None else "N/D" for k, v in data.items()})
        prompt_path = os.path.join(prompts_dir, f"prompt_{i:03d}_{str(data.get('zona','zona')).replace(' ', '_')}.txt")
        with open(prompt_path, "w", encoding="utf-8") as f:
            f.write(prompt)
    logger.info(f"✅ Prompts LLM generati in {prompts_dir}/")
    print(f"\n📊 TOP immobili:\n")
    print(interessanti[["city", "zona", "prezzo", "mq", "prezzo_mq", "score_finale", "verdetto"]]
          .head(10).to_string(index=False))


if __name__ == "__main__":
    main()
