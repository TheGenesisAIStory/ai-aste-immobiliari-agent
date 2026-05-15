# Deployment

## Locale

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

Dashboard:

```bash
pip install -r frontend/requirements.txt
BACKEND_URL=http://127.0.0.1:8000 streamlit run frontend/streamlit_app.py
```

## Variabili Ambiente

```text
APP_ENV=development
DATABASE_URL=sqlite:///./data/processed/app.db
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
LLM_ENABLED=false
LLM_MAX_CHARS=60000
MAX_UPLOAD_MB=15
OCR_MAX_PAGES=10
IMPORT_TIMEOUT_SECONDS=20
IMPORT_MAX_MB=15
BACKEND_URL=http://127.0.0.1:8000
```

`OPENAI_API_KEY` e opzionale. Il fallback rule-based e obbligatorio e non richiede segreti.

## OCR

OCR richiede Tesseract installato nel sistema host/container. Senza Tesseract il backend resta operativo e restituisce warning.

macOS:

```bash
brew install tesseract tesseract-lang
```

Linux Debian/Ubuntu:

```bash
apt-get update && apt-get install -y tesseract-ocr tesseract-ocr-ita
```

## RAG locale

Gli indici locali sono file JSON in `data/processed/rag_index/`. Assicurati che `data/` sia persistente in deploy.

## Docker Compose

```bash
docker compose up
```

Il volume `./data:/app/data` mantiene persistenti DB SQLite e file caricati.

## Produzione

- Imposta `DATABASE_URL` verso storage persistente.
- Usa HTTPS e autenticazione prima di esporre dati reali.
- Valuta cifratura/storage policy: perizie possono contenere dati personali.
- Configura limiti upload e backup DB.
- Non salvare segreti in repository.
- Valuta worker asincroni per PDF grandi o OCR futuro.
