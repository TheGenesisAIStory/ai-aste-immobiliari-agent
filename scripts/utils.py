import logging
import yaml
import os
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_config():
    path = os.path.join(ROOT, "config", "criteri.yaml")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_logger(name: str) -> logging.Logger:
    import colorlog
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        "%(log_color)s%(levelname)s%(reset)s: %(message)s"
    ))
    logger = logging.getLogger(name)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


def ensure_dirs():
    for d in ["data/raw", "data/output"]:
        os.makedirs(os.path.join(ROOT, d), exist_ok=True)


COLONNE_STANDARD = [
    "city", "zona", "link", "prezzo", "mq", "offerta_minima",
    "astato", "occupato", "piano", "ascensore", "spese",
    "classe_energetica", "link_perizia", "note"
]


def normalizza_colonne(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    for col in COLONNE_STANDARD:
        if col not in df.columns:
            df[col] = None
    return df[[col for col in COLONNE_STANDARD if col in df.columns]]
