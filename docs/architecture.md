# Architecture

## Componenti

- `backend/app/main.py`: applicazione FastAPI e registrazione router.
- `backend/app/database.py`: engine SQLAlchemy, session factory, init tabelle e migrazione SQLite minima.
- `backend/app/models.py`: modelli `Valuation`, `DocumentAnalysis`, `ImportRecord`.
- `backend/app/repositories/`: CRUD DB isolato dai router.
- `backend/app/api/`: endpoint valutazioni, import e documenti.
- `backend/app/services/`: scoring, import, OCR, LLM opzionale, RAG locale e Document AI rule-based.
- `frontend/streamlit_app.py`: dashboard operativa che consuma solo API backend.

## Flussi

### Valutazione

`POST /valuate` valida payload, calcola metriche e non salva.  
`POST /valuations` usa la stessa logica e salva il record in DB.

### Import

URL/PDF vengono salvati sotto `data/raw/imports/`, parsati con regole locali e registrati in `import_records`.

### Perizia avanzata

PDF upload -> validazione -> estrazione testo PyMuPDF -> OCR opzionale sulle pagine povere -> normalizzazione -> chunking -> estrazione campi rule-based -> LLM opzionale -> red flag -> summary -> valuation draft -> salvataggio in `document_analyses` -> indice RAG locale.

### RAG

I chunk sono salvati in `data/processed/rag_index/document_{id}.json`.

- senza LLM: keyword retrieval e risposta estrattiva;
- con LLM: risposta generata solo sui chunk recuperati;
- se non trova evidenza: `Non trovato nel documento.`

### Delete

Le delete rimuovono il record DB e provano a rimuovere file fisici associati. Per i documenti eliminano anche i chunk RAG.

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
- `/documents/{id}/ask`
- `/documents/{id}/chunks`
- `/documents/{id}/reindex`
