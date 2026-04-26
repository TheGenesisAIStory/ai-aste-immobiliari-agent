# AI Aste Immobiliari Agent

MVP per valutare aste immobiliari in Italia con backend FastAPI, database SQLAlchemy, dashboard Streamlit con storico persistente, import URL/PDF e analisi perizie rule-based.

Il progetto non fa crawling multipagina, non richiede obbligatoriamente API OpenAI e non inventa dati mancanti: dove le regole non estraggono un campo, il valore resta da completare manualmente.

## Funzionalita

- Valutazione asta con score, margine, ROI, rendimento da affitto e raccomandazione.
- Storico persistente di valutazioni via SQLite locale o PostgreSQL tramite `DATABASE_URL`.
- Import singola pagina URL con salvataggio record e parsing campi asta.
- Upload PDF asta con estrazione testo PyMuPDF, parsing e storico import.
- Analisi perizie PDF con campi estratti, red flag strutturate, sintesi operativa e bozza valutazione.
- Dashboard Streamlit con preview, salvataggio, filtri, detail, delete, export CSV/JSON.

## Setup Locale

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
```

Copia `.env.example` in `.env` se vuoi personalizzare:

```text
APP_ENV=development
DATABASE_URL=sqlite:///./data/processed/app.db
OPENAI_API_KEY=
MAX_UPLOAD_MB=15
BACKEND_URL=http://127.0.0.1:8000
```

## Backend

```bash
source .venv/bin/activate
uvicorn backend.app.main:app --reload
```

Verifiche import:

```bash
python -c "from backend.app.main import app; print(app.title)"
cd backend
python -c "from app.main import app; print(app.title)"
```

Il backend crea automaticamente `data/processed/`, le tabelle DB e, in sviluppo SQLite, aggiunge colonne mancanti non distruttive per mantenere compatibilita con DB locali precedenti.

## Frontend

```bash
source .venv/bin/activate
BACKEND_URL=http://127.0.0.1:8000 streamlit run frontend/streamlit_app.py
```

Tab disponibili:

- Valuta asta
- Storico valutazioni
- Import URL/PDF
- Analisi perizia
- Documenti analizzati
- Info progetto

## Database

Default locale:

```text
DATABASE_URL=sqlite:///./data/processed/app.db
```

Per PostgreSQL usa una URL SQLAlchemy compatibile, per esempio:

```text
DATABASE_URL=postgresql+psycopg2://user:password@host:5432/dbname
```

## Endpoint API

| Metodo | Endpoint | Descrizione |
|---|---|---|
| GET | `/` | Info API |
| GET | `/health` | Health check |
| POST | `/valuate` | Calcola valutazione senza salvare |
| POST | `/valuations` | Calcola e salva valutazione |
| GET | `/valuations` | Lista valutazioni |
| GET | `/valuations/{id}` | Dettaglio valutazione |
| DELETE | `/valuations/{id}` | Elimina record valutazione |
| POST | `/imports/url` | Import singolo URL, parse e salvataggio |
| POST | `/imports/pdf` | Import PDF asta, parse e salvataggio |
| POST | `/imports/parse` | Parsing testo senza salvataggio |
| POST | `/imports/valuate-draft` | Bozza campi per valutazione |
| GET | `/imports` | Lista import |
| GET | `/imports/{id}` | Dettaglio import |
| DELETE | `/imports/{id}` | Elimina record import |
| POST | `/documents/upload` | Upload e analisi perizia PDF con salvataggio |
| GET | `/documents` | Lista documenti analizzati |
| GET | `/documents/{id}` | Dettaglio documento |
| DELETE | `/documents/{id}` | Elimina record documento |

## Esempi Curl

Preview senza salvataggio:

```bash
curl -X POST http://127.0.0.1:8000/valuate \
  -H "Content-Type: application/json" \
  -d '{
    "city": "Torino",
    "zone": "San Donato",
    "address": "Via esempio 10",
    "minimum_bid": 90000,
    "surface_sqm": 80,
    "estimated_market_price_per_sqm": 2500,
    "renovation_cost": 25000,
    "other_costs": 8000,
    "expected_monthly_rent": 850,
    "occupation_status": "libero",
    "legal_risk": "medio",
    "technical_risk": "basso"
  }'
```

Salvataggio storico:

```bash
curl -X POST http://127.0.0.1:8000/valuations \
  -H "Content-Type: application/json" \
  -d @payload.json
```

Liste:

```bash
curl http://127.0.0.1:8000/valuations
curl http://127.0.0.1:8000/imports
curl http://127.0.0.1:8000/documents
```

Import URL:

```bash
curl -X POST http://127.0.0.1:8000/imports/url \
  -H "Content-Type: application/json" \
  -d '{"source_url": "https://example.com/asta"}'
```

Upload PDF asta:

```bash
curl -X POST http://127.0.0.1:8000/imports/pdf \
  -F "file=@avviso.pdf"
```

Upload perizia:

```bash
curl -X POST http://127.0.0.1:8000/documents/upload \
  -F "file=@perizia.pdf"
```

## Docker Compose

```bash
docker compose up
```

Il servizio installa le dipendenze backend e avvia:

```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

## Test

```bash
source .venv/bin/activate
pytest backend/tests
```

La suite copre DB SQLite temporaneo, CRUD valutazioni, 404, `/valuate` non persistente, import URL mockato, import PDF, upload documento, red flag e confidence Document AI.

## Limiti Noti

- Import URL limitato a una sola pagina.
- Nessun crawler o scraping pesante.
- PDF scansiti senza OCR possono produrre testo povero.
- L'analisi documentale e rule-based; `OPENAI_API_KEY` resta opzionale e non necessaria.
- Delete elimina record DB, non file fisici salvati in `data/raw/`.

## Disclaimer

Questo software e un supporto informativo e sperimentale. Non costituisce consulenza finanziaria, legale, fiscale o immobiliare. Prima di partecipare a un'asta verifica perizia, ordinanza, stato occupazionale, vincoli, costi e rischi con professionisti qualificati.
