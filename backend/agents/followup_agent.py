from langchain_google_genai import ChatGoogleGenerativeAI
from config import GOOGLE_API_KEY

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GOOGLE_API_KEY
)


def generate_followup(
    company: str,
    previous_email: str
):

    prompt = f"""
You are an SDR.

Company:
{company}

Original Email:
{previous_email}

Generate:

1. Follow Up #1
2. Follow Up #2
3. Breakup Email

Keep them concise and professional.
"""

    response = llm.invoke(prompt)

    return response.content
