#!/usr/bin/env python3
"""
Script 01 — Normalizza dati grezzi da CSV multipli.
Legge tutti i CSV in data/raw/ e li unisce in data/output/immobili_normalizzati.csv
"""
import os
import glob
import pandas as pd
from utils import load_config, get_logger, ensure_dirs, normalizza_colonne, ROOT

logger = get_logger("01_normalizza")
config = load_config()


def carica_csv_grezzi() -> pd.DataFrame:
    pattern = os.path.join(ROOT, "data", "raw", "*.csv")
    files = glob.glob(pattern)
    if not files:
        logger.warning("Nessun CSV trovato in data/raw/")
        return pd.DataFrame()
    frames = []
    for f in files:
        logger.info(f"Carico: {f}")
        df = pd.read_csv(f, encoding="utf-8")
        df = normalizza_colonne(df)
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def pulizia(df: pd.DataFrame) -> pd.DataFrame:
    # Normalizza city
    df["city"] = df["city"].str.strip().str.title()
    # Normalizza prezzi
    for col in ["prezzo", "offerta_minima", "mq", "spese", "piano"]:
        df[col] = pd.to_numeric(
            df[col].astype(str).str.replace(r"[^\d.]", "", regex=True),
            errors="coerce"
        )
    # Booleani
    for col in ["astato", "occupato", "ascensore"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.lower().isin(["si", "sì", "true", "yes", "1"])
    # Calcolo prezzo al mq
    df["prezzo_mq"] = (df["prezzo"] / df["mq"]).round(0)
    # Zona maiuscola pulita
    df["zona"] = df["zona"].str.strip().str.title()
    # Rimuovi righe senza prezzo o mq
    df = df.dropna(subset=["prezzo", "mq"])
    df = df[df["prezzo"] > 0]
    df = df[df["mq"] > 0]
    return df.reset_index(drop=True)


def main():
    ensure_dirs()
    df = carica_csv_grezzi()
    if df.empty:
        logger.error("Nessun dato caricato. Interrompo.")
        return
    df = pulizia(df)
    out_path = os.path.join(ROOT, "data", "output", "immobili_normalizzati.csv")
    df.to_csv(out_path, index=False, encoding="utf-8")
    logger.info(f"✅ Normalizzati {len(df)} immobili → {out_path}")
    print(df[["city", "zona", "prezzo", "mq", "prezzo_mq", "astato", "occupato"]].to_string(index=False))


if __name__ == "__main__":
    main()
