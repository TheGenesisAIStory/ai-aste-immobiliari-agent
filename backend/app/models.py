from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, Text

from app.database import Base


class TimestampMixin:
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Valuation(Base, TimestampMixin):
    __tablename__ = "valuations"

    id = Column(Integer, primary_key=True, index=True)
    city = Column(String, nullable=False)
    zone = Column(String)
    address = Column(String)
    minimum_bid = Column(Float, nullable=False)
    surface_sqm = Column(Float, nullable=False)
    estimated_market_price_per_sqm = Column(Float, nullable=False)
    renovation_cost = Column(Float, default=0)
    other_costs = Column(Float, default=0)
    expected_monthly_rent = Column(Float, default=0)
    occupation_status = Column(String, default="sconosciuto")
    legal_risk = Column(String, default="medio")
    technical_risk = Column(String, default="medio")
    market_value_estimate = Column(Float, nullable=False)
    total_cost = Column(Float, nullable=False)
    gross_margin = Column(Float, nullable=False)
    gross_roi = Column(Float, nullable=False)
    rental_yield = Column(Float, nullable=False)
    score = Column(Float, nullable=False)
    recommendation = Column(String, nullable=False)
    confidence = Column(String, default="media")
    notes = Column(Text, default="[]")


class DocumentAnalysis(Base, TimestampMixin):
    __tablename__ = "document_analyses"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    saved_path = Column(String, nullable=False)
    page_count = Column(Integer, default=0)
    extracted_text_preview = Column(Text, default="")
    summary = Column(Text, default="")
    extracted_fields_json = Column(Text, default="{}")
    red_flags_json = Column(Text, default="[]")
    missing_fields_json = Column(Text, default="[]")
    confidence = Column(String, default="bassa")


class ImportRecord(Base, TimestampMixin):
    __tablename__ = "import_records"

    id = Column(Integer, primary_key=True, index=True)
    source_type = Column(String, nullable=False)
    source_url = Column(String)
    filename = Column(String)
    saved_path = Column(String)
    extracted_text_preview = Column(Text, default="")
    parsed_fields_json = Column(Text, default="{}")
    risk_keywords_json = Column(Text, default="[]")
    missing_fields_json = Column(Text, default="[]")
    confidence = Column(String, default="bassa")
    status = Column(String, default="ok")
    error_message = Column(Text)
