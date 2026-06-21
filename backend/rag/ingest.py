from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

import os

CHROMA_PATH = "chroma_db"


def ingest_pdf(file_path: str):

    loader = PyPDFLoader(file_path)

    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = splitter.split_documents(
        documents
    )

    company_name = os.path.basename(
        file_path
    ).replace(".pdf", "").lower()

    for chunk in chunks:
        chunk.metadata["company"] = company_name

    if len(chunks) == 0:
        return f"No content found in {file_path}"

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_PATH
    )

    return f"Stored {len(chunks)} chunks for {company_name}"
