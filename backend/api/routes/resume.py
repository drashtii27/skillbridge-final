from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from ...services.pdf_parser import extract_text_from_pdf, clean_resume_text, extract_contact_info
from ...services.llm import extract_skills_from_text
from ...services.analytics import track
from ...db.models import User
from ..deps import get_optional_user

router = APIRouter(prefix="/resume", tags=["resume"])

MAX_PDF_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    user: User | None = Depends(get_optional_user),
):
    if file.content_type not in ("application/pdf", "application/octet-stream"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")
    raw = await file.read()
    if len(raw) > MAX_PDF_SIZE:
        raise HTTPException(status_code=413, detail="File too large (max 10 MB)")

    text = extract_text_from_pdf(raw)
    if not text.strip():
        raise HTTPException(status_code=422, detail="Could not extract text from PDF. Try a different PDF file.")

    text = clean_resume_text(text)
    contact = extract_contact_info(text)
    skills = await extract_skills_from_text(text)

    if user:
        track(str(user.id), "resume_uploaded", {"skills_found": len(skills)})

    return {
        "extracted_skills": skills,
        "contact_info": contact,
        "raw_text_preview": text[:500],
        "char_count": len(text),
    }
