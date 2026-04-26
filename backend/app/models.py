from __future__ import annotations

from sqlalchemy import Column, Integer, String, Float, Text

from app.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String, unique=True, index=True)
    filename = Column(String)
    path = Column(String)
    page_count = Column(Integer)
    risk_level = Column(String)
    red_flags = Column(Text)
    summary = Column(Text)


class Valuation(Base):
    __tablename__ = "valuations"

    id = Column(Integer, primary_key=True, index=True)
    city = Column(String)
    address = Column(String)
    score = Column(Float)
    roi = Column(Float)
    recommendation = Column(String)
