from agents.structured import invoke_structured
from models.outreach import CompanyResearch, LeadScore

def score_lead(research: CompanyResearch) -> LeadScore:

    prompt = f"""
    Based on this company research, assign a lead score from 1-10.

    Consider:
    - Company growth
    - Market opportunity
    - Potential budget
    - Sales opportunity

    Research:
    {research.model_dump_json(indent=2)}
    """

    return invoke_structured(LeadScore, prompt)
