from langchain_google_genai import ChatGoogleGenerativeAI
from config import GOOGLE_API_KEY

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GOOGLE_API_KEY
)


def generate_personalization(
    research: str,
    knowledge: str,
    enrichment: str
):

    prompt = f"""
You are an expert SDR.

Research:
{research}

Company Knowledge:
{knowledge}

Lead Enrichment:
{enrichment}

Create ONE highly personalized outreach angle.

Requirements:
- Mention a likely business challenge
- Mention a likely decision maker
- Mention a likely growth opportunity
- Keep under 60 words
- Sound natural
"""

    response = llm.invoke(prompt)

    return response.content
