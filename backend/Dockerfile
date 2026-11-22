FROM python:3.11-slim AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /build

COPY backend/requirements.txt ./requirements.txt
RUN python -m pip install --prefix=/install -r requirements.txt


FROM python:3.11-slim AS runtime

ENV PATH=/usr/local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    CHROMA_MODEL_CACHE_PATH=/app/.models/all-MiniLM-L6-v2

WORKDIR /app

COPY --from=builder /install /usr/local
COPY backend/ /app/

# Download the embedding model at build time so a fresh container does not
# fetch it when the first user runs the workflow.
RUN python -c "from rag.retriever import ChromaEmbeddings; ChromaEmbeddings().embed_query('warm up')"

RUN addgroup --system app && adduser --system --ingroup app app \
    && mkdir -p /app/uploads /app/chroma_db /app/.models \
    && chown -R app:app /app

USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:' + os.environ.get('PORT', '8000') + '/health', timeout=3)"

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
