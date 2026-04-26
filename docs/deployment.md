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
MAX_UPLOAD_MB=15
BACKEND_URL=http://127.0.0.1:8000
```

`OPENAI_API_KEY` e opzionale. Il fallback rule-based e obbligatorio e non richiede segreti.

## Docker Compose

```bash
docker compose up
```

Il volume `./data:/app/data` mantiene persistenti DB SQLite e file caricati.

## Produzione

- Imposta `DATABASE_URL` verso storage persistente.
- Usa HTTPS e autenticazione prima di esporre dati reali.
- Configura limiti upload e backup DB.
- Non salvare segreti in repository.
- Valuta worker asincroni per PDF grandi o OCR futuro.

