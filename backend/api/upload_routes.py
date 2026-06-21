from fastapi import APIRouter, UploadFile, File
import shutil

from rag.ingest import ingest_pdf

router = APIRouter()


@router.post("/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...)
):

    file_path = f"uploads/{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer
        )

    result = ingest_pdf(file_path)

    return {
        "message": result
    }
