#!/usr/bin/env python3
"""
Script 02 — Calcola score di convenienza, rischio e comparabili.
Input:  data/output/immobili_normalizzati.csv
Output: data/output/immobili_scored.csv
"""
import os
import pandas as pd
from utils import load_config, get_logger, ROOT

logger = get_logger("02_calcola_score")
config = load_config()
pesi = config["pesi_score"]
verdetti = config["verdetti"]


def calcola_comparabile_medio(df: pd.DataFrame) -> pd.DataFrame:
    """
    Per ogni immobile calcola il prezzo medio al mq degli immobili
    NON all'asta nella stessa zona/city come riferimento di mercato.
    """
    normali = df[~df["astato"]].copy()
    comparabili = (
        normali.groupby(["city", "zona"])["prezzo_mq"]
        .mean()
        .round(0)
        .reset_index()
        .rename(columns={"prezzo_mq": "comparabile_avg"})
    )
    df = df.merge(comparabili, on=["city", "zona"], how="left")
    df["discount"] = (
        (df["comparabile_avg"] - df["prezzo_mq"]) / df["comparabile_avg"]
    ).round(3)
    return df


def score_posizione(row: pd.Series, criteri: dict) -> int:
    zone_ok = [z.lower() for z in criteri.get("zone_preferite", [])]
    zone_no = [z.lower() for z in criteri.get("zone_da_evitare", [])]
    zona = str(row.get("zona", "")).lower()
    if any(z in zona for z in zone_no):
        return 20
    if any(z in zona for z in zone_ok):
        return 80
    return 50


def score_qualita(row: pd.Series) -> int:
    score = 50
    if row.get("ascensore"):
        score += 10
    if row.get("piano", 0) >= 2:
        score += 5
    ce = str(row.get("classe_energetica", "")).upper()
    bonus_ce = {"A4": 15, "A3": 12, "A2": 10, "A1": 10, "A": 10, "B": 8, "C": 5, "D": 0, "E": -5, "F": -10, "G": -15}
    score += bonus_ce.get(ce, 0)
    if row.get("spese", 999) <= 80:
        score += 5
    elif row.get("spese", 999) > 150:
        score -= 5
    return max(0, min(100, score))


def score_convenienza(row: pd.Series, criteri: dict) -> int:
    prezzo_mq = row.get("prezzo_mq", 9999)
    target = criteri.get("prezzo_mq_target", 2000)
    massimo = criteri.get("prezzo_mq_max", 3000)
    if prezzo_mq <= target * 0.80:
        base = 90
    elif prezzo_mq <= target:
        base = 75
    elif prezzo_mq <= massimo:
        base = 55
    else:
        base = 25
    discount = row.get("discount", 0) or 0
    if discount > 0.25:
        base = min(100, base + 15)
    elif discount > 0.15:
        base = min(100, base + 8)
    elif discount < 0:
        base = max(0, base - 15)
    return int(base)


def score_liquidabilita(row: pd.Series, criteri: dict) -> int:
    score = 55
    if row.get("ascensore"):
        score += 10
    if row.get("piano", 0) >= 2:
        score += 5
    if row.get("spese", 999) <= 100:
        score += 5
    ce = str(row.get("classe_energetica", "")).upper()
    if ce in ["A4", "A3", "A2", "A1", "A", "B", "C"]:
        score += 10
    elif ce in ["F", "G"]:
        score -= 15
    return max(0, min(100, score))


def score_rischio(row: pd.Series) -> int:
    """
    Score rischio: PIÙ basso = meglio (0 = nessun rischio, 100 = rischio massimo)
    """
    rischio = 20
    if row.get("astato") and row.get("occupato"):
        rischio += 35
    elif row.get("astato"):
        rischio += 15
    if not row.get("link_perizia"):
        rischio += 20
    if row.get("classe_energetica", "").upper() in ["F", "G"]:
        rischio += 15
    if row.get("spese", 0) > 200:
        rischio += 10
    return max(0, min(100, rischio))


def verdetto_finale(score: float) -> str:
    if score >= verdetti["offerta"]:
        return "💚 OFFERTA"
    elif score >= verdetti["approfondisci"]:
        return "🟡 APPROFONDISCI"
    elif score >= verdetti["monitora"]:
        return "🟠 MONITORA"
    else:
        return "🔴 SCARTA"


def applica_scores(df: pd.DataFrame) -> pd.DataFrame:
    scores = []
    for _, row in df.iterrows():
        city = str(row.get("city", "")).lower()
        criteri = config.get(city, config.get("torino"))
        s_pos = score_posizione(row, criteri)
        s_qua = score_qualita(row)
        s_con = score_convenienza(row, criteri)
        s_liq = score_liquidabilita(row, criteri)
        s_ris = score_rischio(row)
        score_fin = round(
            s_pos * pesi["posizione"]
            + s_qua * pesi["qualita_immobile"]
            + s_con * pesi["convenienza_economica"]
            + s_liq * pesi["liquidabilita"]
            - s_ris * pesi["rischio"],  # rischio è penalizzante
            1
        )
        score_fin = max(0, min(100, score_fin))
        scores.append({
            "s_posizione": s_pos,
            "s_qualita": s_qua,
            "s_convenienza": s_con,
            "s_liquidabilita": s_liq,
            "s_rischio": s_ris,
            "score_finale": score_fin,
            "verdetto": verdetto_finale(score_fin)
        })
    return pd.concat([df.reset_index(drop=True), pd.DataFrame(scores)], axis=1)


def main():
    in_path = os.path.join(ROOT, "data", "output", "immobili_normalizzati.csv")
    if not os.path.exists(in_path):
        logger.error(f"File non trovato: {in_path} — esegui prima 01_normalizza_dati.py")
        return
    df = pd.read_csv(in_path, encoding="utf-8")
    df = calcola_comparabile_medio(df)
    df = applica_scores(df)
    out_path = os.path.join(ROOT, "data", "output", "immobili_scored.csv")
    df.to_csv(out_path, index=False, encoding="utf-8")
    logger.info(f"✅ Scored {len(df)} immobili → {out_path}")
    cols = ["city", "zona", "prezzo_mq", "comparabile_avg", "discount", "score_finale", "verdetto"]
    print(df[[c for c in cols if c in df.columns]].sort_values("score_finale", ascending=False).to_string(index=False))


if __name__ == "__main__":
    main()
