from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import shutil
import os

from rag.ingest import ingest_pdf
from graph.workflow import run_pipeline
from database.crud import save_lead

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...)
):

    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(
                file.file,
                buffer
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save file: {str(e)}"
        )

    try:
        result = ingest_pdf(file_path)
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

    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )

    pdf_filename = f"{company.lower().replace(' ', '_')}.pdf"
    file_path = os.path.join(UPLOAD_DIR, pdf_filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save file: {str(e)}"
        )

    try:
        ingest_pdf(file_path)
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
