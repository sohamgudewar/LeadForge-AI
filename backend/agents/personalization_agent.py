from langchain_google_genai import ChatGoogleGenerativeAI
from config import GOOGLE_API_KEY

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GOOGLE_API_KEY
)

def generate_personalization(research_summary: str):

    prompt = f"""
    You are a sales development representative.

    Based on the company research below:

    {research_summary}

    Create a short personalized outreach hook.

    Rules:
    - Maximum 2 sentences
    - Professional
    - Mention a likely challenge
    - Mention a possible opportunity

    Return only the hook.
    """

    response = llm.invoke(prompt)

    return response.content
