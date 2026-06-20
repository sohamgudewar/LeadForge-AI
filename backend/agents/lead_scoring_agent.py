from langchain_google_genai import ChatGoogleGenerativeAI
from config import GOOGLE_API_KEY

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GOOGLE_API_KEY
)

def score_lead(research: str):

    prompt = f"""
    Based on this company research, assign a lead score from 1-10.

    Consider:
    - Company growth
    - Market opportunity
    - Potential budget
    - Sales opportunity

    Research:
    {research}

    Return ONLY:

    Score: X/10

    Reason:
    ...
    """

    response = llm.invoke(prompt)

    return response.content
