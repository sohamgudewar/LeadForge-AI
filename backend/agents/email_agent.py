from config import get_llm

llm = get_llm()


def generate_email(company_name: str, personalization: str):

    prompt = f"""
    Write a cold outreach email.

    Company:
    {company_name}

    Personalization:
    {personalization}

    Rules:
    - Subject line included
    - Under 120 words
    - Professional
    - Clear CTA

    Format:

    Subject:
    ...

    Email:
    ...
    """

    response = llm.invoke(prompt)

    return response.content
