# AI Aste Immobiliari Agent

MVP per valutare aste immobiliari in Italia con backend FastAPI, dashboard Streamlit, import singola pagina URL/PDF, analisi documenti rule-based e base dati SQLite.

Il progetto non esegue crawler e non richiede obbligatoriamente API OpenAI: le funzioni attuali usano regole semplici e trasparenti per produrre una prima valutazione operativa.

## Funzionalita

- Valutazione economica asta con score, rendimento lordo, sconto stimato e raccomandazione.
- Import di una singola pagina URL con estrazione testo via BeautifulSoup.
- Upload PDF asta con estrazione testo via PyMuPDF.
- Parsing MVP di testi d'asta per campi come citta, indirizzo, offerta minima, mq, data asta e tribunale.
- Upload documento/perizia PDF con chunking, parole chiave di rischio e livello rischio.
- Persistenza predisposta con SQLAlchemy e SQLite.
- Dashboard Streamlit che chiama il backend via `BACKEND_URL` e gestisce backend offline.

## Struttura Repo

```text
ai-aste-immobiliari-agent/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── api/
│   │   │   ├── imports.py
│   │   │   └── documents.py
│   │   ├── services/
│   │   │   ├── scoring_service.py
│   │   │   ├── import_service.py
│   │   │   ├── parser_service.py
│   │   │   ├── document_service.py
│   │   │   └── document_agent.py
│   │   └── schemas/
│   │       ├── auction_schema.py
│   │       ├── import_schema.py
│   │       └── document_schema.py
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── streamlit_app.py
│   └── requirements.txt
├── data/
│   ├── raw/
│   └── processed/
├── docker-compose.yml
├── README.md
├── .env.example
└── .gitignore
```

Le cartelle legacy `scripts/`, `prompts/`, `examples/` e `config/` restano nel repository come materiale utile della pipeline iniziale.

## Quick Start Backend

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload
```

Verifica:

```bash
python -c "from backend.app.main import app; print(app.title)"
cd backend
python -c "from app.main import app; print(app.title)"
```

## Quick Start Frontend

```bash
source .venv/bin/activate
pip install -r frontend/requirements.txt
BACKEND_URL=http://127.0.0.1:8000 streamlit run frontend/streamlit_app.py
```

Se `BACKEND_URL` non e impostato, la dashboard usa `http://127.0.0.1:8000`.

## Endpoint API

| Metodo | Endpoint | Descrizione |
|---|---|---|
| GET | `/` | Info base API |
| GET | `/health` | Health check |
| POST | `/valuate` | Valutazione asta |
| POST | `/imports/url` | Import singola pagina URL |
| POST | `/imports/pdf` | Import PDF asta |
| POST | `/imports/parse` | Parsing testo asta |
| POST | `/imports/valuate-draft` | Bozza campi per valutazione |
| POST | `/documents/upload` | Upload e analisi documento PDF |

### Esempio `/valuate`

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

### Esempio import URL

```bash
curl -X POST http://127.0.0.1:8000/imports/url \
  -H "Content-Type: application/json" \
  -d '{"source_url": "https://example.com/asta"}'
```

### Esempio upload PDF

```bash
curl -X POST http://127.0.0.1:8000/imports/pdf \
  -F "file=@perizia.pdf"
```

## Configurazione `.env`

Copia `.env.example` in `.env` se vuoi personalizzare:

```text
DATABASE_URL=sqlite:///./data/processed/app.db
BACKEND_URL=http://127.0.0.1:8000
```

Il backend crea automaticamente le cartelle e le tabelle SQLite necessarie all'avvio o al primo uso.

## Note su PDF e URL

- L'import URL scarica una sola pagina, senza crawling.
- Il PDF massimo accettato e 15 MB.
- I file importati vengono salvati sotto `data/raw/imports/` o `data/raw/documents/`.
- L'estrazione testo dipende dalla qualita del PDF: scansioni senza OCR possono produrre testo vuoto.

## Test

```bash
source .venv/bin/activate
pytest backend/tests
```

I test coprono health check, valutazione, parsing testo, import PDF e upload documento PDF.

## Deploy Base

Avvio locale con Docker Compose:

```bash
docker compose up
```

Per un deploy applicativo, esporre il backend FastAPI con:

```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

e configurare `DATABASE_URL` verso SQLite persistente o un database compatibile SQLAlchemy.

## Roadmap

- Salvare valutazioni, import e documenti in database tramite repository dedicati.
- Aggiungere autenticazione e gestione utenti.
- Migliorare parser documenti con OCR opzionale.
- Introdurre comparabili di mercato verificati e aggiornabili.
- Aggiungere job asincroni per import PDF pesanti.
- Preparare CI GitHub Actions con lint e test.

## Disclaimer

Questo software e un supporto informativo e sperimentale. Non costituisce consulenza finanziaria, legale, fiscale o immobiliare. Prima di partecipare a un'asta verifica sempre perizia, ordinanza, stato occupazionale, vincoli, costi e rischi con professionisti qualificati.
