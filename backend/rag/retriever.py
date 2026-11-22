from langchain_chroma import Chroma
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
from chromadb.utils.embedding_functions.onnx_mini_lm_l6_v2 import ONNXMiniLM_L6_V2
import os
from pathlib import Path
import tempfile

CHROMA_PATH = str(Path(__file__).resolve().parents[1] / "chroma_db")
MODEL_CACHE_PATH = Path(
    os.getenv(
        "CHROMA_MODEL_CACHE_PATH",
        str(Path(tempfile.gettempdir()) / "chroma" / "onnx_models" / ONNXMiniLM_L6_V2.MODEL_NAME),
    )
)

# Render services can have HOME=/nonexistent. Chroma otherwise derives its ONNX
# download directory from HOME and fails before the first similarity search.
ONNXMiniLM_L6_V2.DOWNLOAD_PATH = MODEL_CACHE_PATH

_vectorstore = None

# Searching with only the company name returns near-arbitrary chunks, because
# every chunk of that company's PDF mentions the company. Instead we ask the
# questions the downstream agents actually need answered, then merge results.
RETRIEVAL_QUERIES = (
    "{company} products, services and what the company does",
    "{company} customers, target market and positioning",
    "{company} challenges, goals, priorities and growth plans",
)
TOP_K_PER_QUERY = 2
MAX_CONTEXT_CHUNKS = 5


class ChromaEmbeddings:
    def __init__(self):
        self._ef = DefaultEmbeddingFunction()

    def embed_query(self, text: str) -> list[float]:
        result = self._ef([text])
        return [float(x) for x in result[0]]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        result = self._ef(texts)
        return [[float(x) for x in emb] for emb in result]


def _get_vectorstore():
    global _vectorstore
    if _vectorstore is None:
        _vectorstore = Chroma(
            persist_directory=CHROMA_PATH,
            embedding_function=ChromaEmbeddings()
        )
    return _vectorstore


def normalize_company(company: str) -> str:
    """Single source of truth for the company metadata key (ingest + retrieve)."""
    return " ".join(company.split()).lower()


def retrieve_company_context(company: str) -> str:

    vs = _get_vectorstore()
    company_key = normalize_company(company)

    # Most companies have no uploaded PDF. A metadata lookup answers that
    # without running the embedding model, which takes ~17 s for three queries
    # on a small CPU.
    if not vs.get(where={"company": company_key}, limit=1, include=[])["ids"]:
        return "No company knowledge found."

    # Embed all queries in one batch instead of one model call per query.
    queries = [template.format(company=company) for template in RETRIEVAL_QUERIES]
    vectors = vs.embeddings.embed_documents(queries)

    seen: set[str] = set()
    chunks: list[str] = []
    for vector in vectors:
        docs = vs.similarity_search_by_vector(
            embedding=vector,
            k=TOP_K_PER_QUERY,
            filter={"company": company_key},
        )
        for doc in docs:
            if doc.page_content not in seen:
                seen.add(doc.page_content)
                chunks.append(doc.page_content)

    if not chunks:
        return "No company knowledge found."

    return "\n\n".join(chunks[:MAX_CONTEXT_CHUNKS])
