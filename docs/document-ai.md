# Document AI

## Pipeline

1. Upload PDF.
2. Validazione estensione e dimensione (`MAX_UPLOAD_MB`).
3. Estrazione testo nativa con PyMuPDF.
4. OCR opzionale con Tesseract sulle pagine con testo insufficiente.
5. Normalizzazione e chunking.
6. Estrazione campi rule-based.
7. LLM opzionale se `LLM_ENABLED=true` e `OPENAI_API_KEY` presente.
8. Red flag strutturate con evidence.
9. Summary non inventato.
10. Indicizzazione RAG locale.

## OCR

Variabile:

```text
OCR_MAX_PAGES=10
```

Metadata restituiti: `ocr_used`, `ocr_pages`, `text_extraction_method`, `warnings`.

Se Tesseract non e installato, l'API non va in crash.

## LLM Opzionale

```text
LLM_ENABLED=false
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
LLM_MAX_CHARS=60000
```

Il prompt impone di estrarre solo dati presenti, non stimare dati economici, citare evidence breve, restituire JSON validabile e fare fallback rule-based in caso di errore.

## RAG locale

Endpoint:

```text
POST /documents/{document_id}/ask
GET  /documents/{document_id}/chunks
POST /documents/{document_id}/reindex
```

Il fallback offline usa keyword retrieval. Il Q&A non usa conoscenza esterna: se l'informazione non e nei chunk, risponde `Non trovato nel documento.`

## Privacy

Le perizie possono contenere dati personali o sensibili. In locale i PDF sono salvati sotto `data/raw/documents/` e i chunk sotto `data/processed/rag_index/`. Evita di caricare documenti reali in ambienti non protetti.
