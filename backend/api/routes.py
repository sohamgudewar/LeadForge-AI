from fastapi import APIRouter, HTTPException

from models.lead import LeadRequest

from graph.workflow import run_pipeline

from database.crud import (
    save_lead,
    get_leads,
    get_lead_by_id
)

router = APIRouter()


@router.post("/run-agent")
def run_agent(request: LeadRequest):

    result = run_pipeline(request.company)

    try:
        save_lead(result)
    except Exception as e:
        return {
            **result,
            "warning": f"Lead processed but could not be saved: {str(e)}"
        }

    return result


@router.get("/leads")
def fetch_leads():

    try:
        leads = get_leads()
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Database unavailable: {str(e)}"
        )

    return [
        {
            "id": lead.id,
            "company": lead.company
        }
        for lead in leads
    ]


@router.get("/lead/{lead_id}")
def fetch_lead(lead_id: int):

    try:
        lead = get_lead_by_id(lead_id)
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Database unavailable: {str(e)}"
        )

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
