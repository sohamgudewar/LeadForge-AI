from contextlib import asynccontextmanager
import logging
import os
import threading

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.upload_routes import router as upload_router
from api.routes import router
from database.models import Base
from database.db import engine


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("leadforge")


def _warm_up() -> None:
    """Load the embedding model and Gemini client before the first request.

    Without this, the first user after a deploy pays for loading the ONNX
    embedding model and creating the client. It runs in a background thread
    so the health check is not delayed.
    """
    try:
        from rag.retriever import _get_vectorstore

        _get_vectorstore().embeddings.embed_query("warm up")
    except Exception:
        logger.exception("Embedding warm-up failed")
    try:
        from config import get_llm

        get_llm()
    except Exception:
        logger.exception("LLM client warm-up failed")


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    if os.getenv("SKIP_WARMUP") != "1":
        threading.Thread(target=_warm_up, daemon=True).start()
    yield


app = FastAPI(
    title="LeadForge AI",
    lifespan=lifespan
)

default_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://leadforgeai0i0.vercel.app",
]
configured_origins = [
    origin.strip().rstrip("/")
    for origin in os.getenv("CORS_ORIGINS", "").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=configured_origins or default_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(router)
app.include_router(upload_router)
