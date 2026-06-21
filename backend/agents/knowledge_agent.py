from rag.retriever import retrieve_company_context


def get_company_knowledge(company: str):

    result = retrieve_company_context(
        company
    )

    return result
