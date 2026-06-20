from langchain_google_genai import ChatGoogleGenerativeAI
from config import GOOGLE_API_KEY

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GOOGLE_API_KEY
)


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
