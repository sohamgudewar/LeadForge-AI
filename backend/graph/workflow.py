from graph.state import SDRState

from agents.knowledge_agent import get_company_knowledge
from agents.research_agent import research_company
from agents.enrichment_agent import enrich_lead
from agents.lead_scoring_agent import score_lead
from agents.personalization_agent import generate_personalization
from agents.email_agent import generate_email
from agents.reviewer_agent import review_outreach


def run_pipeline(company: str) -> dict:
    state: SDRState = {
        "company": company,
        "knowledge": "",
        "research": "",
        "enrichment": "",
        "lead_score": "",
        "personalization": "",
        "email": "",
        "review": "",
    }

    state["knowledge"] = get_company_knowledge(state["company"])
    state["research"] = research_company(state["company"])
    state["enrichment"] = enrich_lead(state["company"])
    state["lead_score"] = score_lead(state["research"])
    state["personalization"] = generate_personalization(
        state["research"], state["knowledge"], state["enrichment"]
    )
    state["email"] = generate_email(state["company"], state["personalization"])
    state["review"] = review_outreach(
        state["research"], state["personalization"], state["email"]
    )

    return state
