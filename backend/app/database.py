from __future__ import annotations

import os
from pathlib import Path
from typing import Generator, Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker
from sqlalchemy import text

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/processed/app.db")

Base = declarative_base()
engine: Engine
SessionLocal: sessionmaker


def _ensure_sqlite_parent(database_url: str) -> None:
    if not database_url.startswith("sqlite"):
        return
    db_path = database_url.replace("sqlite:///", "", 1)
    if db_path not in {":memory:", ""}:
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)


def _make_engine(database_url: str) -> Engine:
    _ensure_sqlite_parent(database_url)
    if database_url.startswith("sqlite"):
        return create_engine(database_url, connect_args={"check_same_thread": False})
    return create_engine(database_url)


def configure_database(database_url: Optional[str] = None) -> None:
    global DATABASE_URL, SessionLocal, engine
    DATABASE_URL = database_url or os.getenv("DATABASE_URL", "sqlite:///./data/processed/app.db")
    engine = _make_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


configure_database(DATABASE_URL)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _migrate_sqlite_dev_schema()


def _migrate_sqlite_dev_schema() -> None:
    if not DATABASE_URL.startswith("sqlite"):
        return

    expected_columns = {
        "valuations": {
            "zone": "VARCHAR",
            "minimum_bid": "FLOAT",
            "surface_sqm": "FLOAT",
            "estimated_market_price_per_sqm": "FLOAT",
            "renovation_cost": "FLOAT",
            "other_costs": "FLOAT",
            "expected_monthly_rent": "FLOAT",
            "occupation_status": "VARCHAR",
            "legal_risk": "VARCHAR",
            "technical_risk": "VARCHAR",
            "market_value_estimate": "FLOAT",
            "total_cost": "FLOAT",
            "gross_margin": "FLOAT",
            "gross_roi": "FLOAT",
            "rental_yield": "FLOAT",
            "confidence": "VARCHAR",
            "notes": "TEXT",
            "created_at": "DATETIME",
            "updated_at": "DATETIME",
        }
    }
    with engine.begin() as connection:
        for table, columns in expected_columns.items():
            existing = {
                row[1]
                for row in connection.execute(text(f"PRAGMA table_info({table})")).fetchall()
            }
            if not existing:
                continue
            for column, column_type in columns.items():
                if column not in existing:
                    connection.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {column_type}"))
