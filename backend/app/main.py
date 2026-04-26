from __future__ import annotations

import sys
from pathlib import Path

from fastapi import FastAPI

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.api import documents, imports, valuations  # noqa: E402
from app.database import init_db  # noqa: E402
from app.schemas.auction_schema import AuctionValuationRequest, AuctionValuationResponse  # noqa: E402
from app.services.scoring_service import valuate_auction  # noqa: E402

app = FastAPI(
    title="AI Aste Immobiliari Agent",
    version="0.1.0",
    description="MVP API per valutazione aste immobiliari, import URL/PDF e analisi documenti.",
)


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/")
def root() -> dict[str, str]:
    return {"name": app.title, "status": "ok"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/valuate", response_model=AuctionValuationResponse)
def valuate(payload: AuctionValuationRequest) -> AuctionValuationResponse:
    return valuate_auction(payload)


app.include_router(imports.router)
app.include_router(documents.router)
app.include_router(valuations.router)

init_db()
