from agents.structured import invoke_structured
from models.outreach import LeadEnrichment


def enrich_lead(company: str) -> LeadEnrichment:

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

    return invoke_structured(LeadEnrichment, prompt)
