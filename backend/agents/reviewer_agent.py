from langchain_google_genai import ChatGoogleGenerativeAI
from config import GOOGLE_API_KEY

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GOOGLE_API_KEY
)


def review_outreach(
    research: str,
    personalization: str,
    email: str
):

    prompt = f"""
You are a senior SDR manager.

Review the following outreach package.

Research:
{research}

Personalization:
{personalization}

Email:
{email}

Evaluate:

1. Research Quality (1-10)
2. Personalization Quality (1-10)
3. Email Quality (1-10)
4. Overall SDR Readiness Score

Give strengths and weaknesses.

Keep response concise.
"""

    response = llm.invoke(prompt)

    return response.content
