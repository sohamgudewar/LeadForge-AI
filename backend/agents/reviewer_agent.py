from config import get_llm

llm = get_llm()


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
