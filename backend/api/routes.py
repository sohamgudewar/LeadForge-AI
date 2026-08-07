import json

from fastapi import APIRouter, HTTPException

from models.lead import LeadRequest

from graph.workflow import run_pipeline

from database.crud import (
    save_lead,
    get_leads,
    get_lead_by_id
)

router = APIRouter()


def _decode_structured(value):
    if not isinstance(value, str):
        return value
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value


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
        raise HTTPException(status_code=404, detail="Lead not found")

    return {
        "id": lead.id,
        "company": lead.company,
        "knowledge": lead.knowledge,
        "research": _decode_structured(lead.research),
        "enrichment": _decode_structured(lead.enrichment),
        "lead_score": _decode_structured(lead.lead_score),
        "personalization": _decode_structured(lead.personalization),
        "email": _decode_structured(lead.email),
        "review": _decode_structured(lead.review)
    }
