from config import get_llm

llm = get_llm()


def research_company(company_name: str):

    prompt = f"""
    Analyze the company: {company_name}

    Return:

    1. Industry
    2. Possible business challenges
    3. Potential sales opportunities

    Keep response concise.
    """

    response = llm.invoke(prompt)

    return response.content
