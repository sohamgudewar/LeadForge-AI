from config import get_llm

llm = get_llm()


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
