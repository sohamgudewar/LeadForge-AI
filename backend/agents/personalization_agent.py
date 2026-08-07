from agents.structured import invoke_structured
from models.outreach import CompanyResearch, LeadEnrichment, Personalization


def generate_personalization(
    research: CompanyResearch,
    knowledge: str,
    enrichment: LeadEnrichment
) -> Personalization:

    prompt = f"""
You are an expert SDR.

Research:
{research.model_dump_json(indent=2)}

Company Knowledge:
{knowledge}

Lead Enrichment:
{enrichment.model_dump_json(indent=2)}

Create ONE highly personalized outreach angle.

Requirements:
- Mention a likely business challenge
- Mention a likely decision maker
- Mention a likely growth opportunity
- Keep under 60 words
- Sound natural
"""

    return invoke_structured(Personalization, prompt)
