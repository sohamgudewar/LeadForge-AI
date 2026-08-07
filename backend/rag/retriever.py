from langchain_chroma import Chroma
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
from pathlib import Path

CHROMA_PATH = str(Path(__file__).resolve().parents[1] / "chroma_db")

_vectorstore = None


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


def retrieve_company_context(company: str):

    vs = _get_vectorstore()

    docs = vs.similarity_search(
        query=company,
        k=3,
        filter={
            "company": company.lower()
        }
    )

    if not docs:
        return "No company knowledge found."

    return "\n".join(
        [doc.page_content for doc in docs]
    )
