from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

CHROMA_PATH = "chroma_db"

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vectorstore = Chroma(
    persist_directory=CHROMA_PATH,
    embedding_function=embeddings
)


def retrieve_company_context(company: str):

    docs = vectorstore.similarity_search(
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
