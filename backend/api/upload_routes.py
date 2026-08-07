from pathlib import Path
import re
from uuid import uuid4

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import ValidationError

from rag.ingest import ingest_pdf
from graph.workflow import run_pipeline
from database.crud import save_lead
from models.lead import LeadRequest

router = APIRouter()

UPLOAD_DIR = Path(__file__).resolve().parents[1] / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MAX_PDF_SIZE = 10 * 1024 * 1024
PDF_CONTENT_TYPES = {"application/pdf", "application/x-pdf"}


def _safe_stem(value: str) -> str:
    stem = re.sub(r"[^a-zA-Z0-9_-]+", "_", value).strip("_-").lower()
    return stem[:80] or "document"


async def _save_pdf(file: UploadFile, stem: str) -> Path:
    filename = file.filename or ""
    if Path(filename).suffix.lower() != ".pdf":
        await file.close()
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    if file.content_type not in PDF_CONTENT_TYPES:
        await file.close()
        raise HTTPException(status_code=400, detail="File content type must be PDF")

    first_chunk = await file.read(1024 * 1024)
    if not first_chunk.startswith(b"%PDF-"):
        await file.close()
        raise HTTPException(status_code=400, detail="File content is not a valid PDF")

    file_path = UPLOAD_DIR / f"{_safe_stem(stem)}-{uuid4().hex}.pdf"
    total_size = len(first_chunk)
    try:
        with file_path.open("wb") as buffer:
            buffer.write(first_chunk)
            while chunk := await file.read(1024 * 1024):
                total_size += len(chunk)
                if total_size > MAX_PDF_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail="PDF must be 10 MB or smaller"
                    )
                buffer.write(chunk)
    except Exception:
        file_path.unlink(missing_ok=True)
        raise
    finally:
        await file.close()
    return file_path


@router.post("/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...)
):

    file_path = await _save_pdf(file, Path(file.filename or "document").stem)

    try:
        result = ingest_pdf(str(file_path))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process PDF: {str(e)}"
        )

    return {
        "message": result
    }


@router.post("/run-agent-with-pdf")
async def run_agent_with_pdf(
    company: str = Form(...),
    file: UploadFile = File(...)
):

    try:
        company = LeadRequest(company=company).company
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors()) from exc

    file_path = await _save_pdf(file, company)

    try:
        ingest_pdf(str(file_path), company_name=company)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process PDF: {str(e)}"
        )

    try:
        result = run_pipeline(company)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Agent pipeline failed: {str(e)}"
        )

    try:
        save_lead(result)
    except Exception as e:
        result["warning"] = f"Lead processed but could not be saved: {str(e)}"

    return result
