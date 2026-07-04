from config import get_llm

llm = get_llm()


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
