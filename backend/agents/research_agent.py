from langchain_google_genai import ChatGoogleGenerativeAI
from config import GOOGLE_API_KEY

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GOOGLE_API_KEY
)

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
