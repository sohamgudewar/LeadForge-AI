from config import get_llm

llm = get_llm()

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
