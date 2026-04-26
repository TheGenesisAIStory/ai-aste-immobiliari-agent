# Architecture

## Componenti

- `backend/app/main.py`: applicazione FastAPI e registrazione router.
- `backend/app/database.py`: engine SQLAlchemy, session factory, init tabelle e migrazione SQLite minima.
- `backend/app/models.py`: modelli `Valuation`, `DocumentAnalysis`, `ImportRecord`.
- `backend/app/repositories/`: CRUD DB isolato dai router.
- `backend/app/api/`: endpoint valutazioni, import e documenti.
- `backend/app/services/`: scoring, import, parsing PDF/URL e Document AI rule-based.
- `frontend/streamlit_app.py`: dashboard operativa che consuma solo API backend.

## Flussi

### Valutazione

`POST /valuate` valida payload, calcola metriche e non salva.  
`POST /valuations` usa la stessa logica e salva il record in DB.

### Import

URL/PDF vengono salvati sotto `data/raw/imports/`, parsati con regole locali e registrati in `import_records`.

### Perizia

PDF upload -> validazione -> estrazione testo PyMuPDF -> normalizzazione -> chunking -> estrazione campi -> red flag -> summary -> valuation draft -> salvataggio in `document_analyses`.

## Database

Default: `sqlite:///./data/processed/app.db`.  
PostgreSQL e supportato tramite `DATABASE_URL`, usando driver compatibile installato nell'ambiente di deploy.

## Compatibilita

Endpoint MVP mantenuti:

- `/health`
- `/valuate`
- `/imports/url`
- `/imports/pdf`
- `/imports/parse`
- `/documents/upload`

