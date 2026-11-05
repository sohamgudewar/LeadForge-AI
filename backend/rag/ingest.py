from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

import hashlib
import os

from rag.retriever import _get_vectorstore, normalize_company


def chunk_id(company_name: str, content: str) -> str:
    """Deterministic ID: same company + same text always maps to the same ID."""
    return hashlib.sha256(f"{company_name}\x00{content}".encode("utf-8")).hexdigest()


def ingest_pdf(file_path: str, company_name: str | None = None):

    loader = PyPDFLoader(file_path)

    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = splitter.split_documents(
        documents
    )

    company_name = normalize_company(
        company_name
        or os.path.splitext(os.path.basename(file_path))[0]
    )

    for chunk in chunks:
        chunk.metadata["company"] = company_name

    if len(chunks) == 0:
        return f"No content found in {file_path}"

    # Chroma upserts by ID, so re-uploading the same PDF overwrites its chunks
    # instead of duplicating them (duplicates would crowd out other results).
    unique = {chunk_id(company_name, chunk.page_content): chunk for chunk in chunks}

    _get_vectorstore().add_documents(
        documents=list(unique.values()),
        ids=list(unique.keys()),
    )

    return f"Stored {len(unique)} chunks for {company_name}"
