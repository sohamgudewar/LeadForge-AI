from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

import os

from rag.retriever import CHROMA_PATH, ChromaEmbeddings


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

    company_name = (
        company_name
        or os.path.splitext(os.path.basename(file_path))[0]
    ).strip().lower()

    for chunk in chunks:
        chunk.metadata["company"] = company_name

    if len(chunks) == 0:
        return f"No content found in {file_path}"

    embeddings = ChromaEmbeddings()

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_PATH
    )

    return f"Stored {len(chunks)} chunks for {company_name}"
