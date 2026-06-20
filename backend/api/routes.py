from fastapi import APIRouter

from models.lead import LeadRequest

from graph.workflow import graph

from database.crud import (
    save_lead,
    get_leads,
    get_lead_by_id
)

router = APIRouter()


@router.post("/run-agent")
def run_agent(request: LeadRequest):

    result = graph.invoke(
        {
            "company": request.company
        }
    )

    save_lead(result)

    return result


@router.get("/leads")
def fetch_leads():

    leads = get_leads()

    return [
        {
            "id": lead.id,
            "company": lead.company
        }
        for lead in leads
    ]


@router.get("/lead/{lead_id}")
def fetch_lead(lead_id: int):

    lead = get_lead_by_id(lead_id)

    if not lead:
        return {
            "error": "Lead not found"
        }

    return {
        "id": lead.id,
        "company": lead.company,
        "knowledge": lead.knowledge,
        "research": lead.research,
        "enrichment": lead.enrichment,
        "lead_score": lead.lead_score,
        "personalization": lead.personalization,
        "email": lead.email,
        "review": lead.review
    }
