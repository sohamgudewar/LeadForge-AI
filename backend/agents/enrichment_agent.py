from langchain_google_genai import ChatGoogleGenerativeAI
from config import GOOGLE_API_KEY

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GOOGLE_API_KEY
)


def enrich_lead(company: str):

    prompt = f"""
Company:
{company}

Provide:

1. Estimated company size
2. Possible target buyers
3. Common departments using sales tools
4. Potential decision makers
5. Estimated outreach priority

Keep concise.
"""

    response = llm.invoke(prompt)

    return response.content
