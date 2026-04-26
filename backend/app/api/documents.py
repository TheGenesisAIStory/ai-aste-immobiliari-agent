from fastapi import APIRouter, UploadFile, File, HTTPException

from app.services.document_service import save_pdf, extract_text, chunk_text
from app.services.document_agent import analyze_document

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Solo PDF consentiti")

    content = await file.read()
    if len(content) > 15 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File troppo grande")

    doc_id, path = save_pdf(content, file.filename)
    text, pages = extract_text(path)

    chunks = chunk_text(text)
    analysis = analyze_document(text)

    return {
        "document_id": doc_id,
        "filename": file.filename,
        "status": "ok",
        "page_count": pages,
        "saved_path": path,
        "text_preview": text[:500],
        "chunks": [
            {"index": i, "text_preview": c[:200], "char_count": len(c)}
            for i, c in enumerate(chunks)
        ],
        "extracted_sections": analysis["sections"],
        "red_flags": analysis["red_flags"],
        "risk_level": analysis["risk_level"],
        "confidence": analysis["confidence"],
        "notes": analysis["notes"],
    }
