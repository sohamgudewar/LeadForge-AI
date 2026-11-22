import json
import os
import threading
import time

from fastapi import APIRouter, Depends, HTTPException

from api.rate_limit import enforce_run_limit

from models.lead import LeadRequest

from graph.workflow import run_pipeline

from database.crud import (
    save_lead,
    get_leads,
    get_lead_by_id
)

router = APIRouter()

# Repeat requests for the same company within this window return the previous
# result instantly instead of re-running every model call. 0 disables it.
RESULT_CACHE_TTL_SECONDS = int(os.getenv("RESULT_CACHE_TTL_SECONDS", "3600"))
_result_cache: dict[str, tuple[float, dict]] = {}
_result_cache_lock = threading.Lock()


def _cache_key(company: str) -> str:
    return " ".join(company.split()).lower()


def _get_cached_result(company: str) -> dict | None:
    if RESULT_CACHE_TTL_SECONDS <= 0:
        return None
    key = _cache_key(company)
    with _result_cache_lock:
        entry = _result_cache.get(key)
        if entry is None:
            return None
        stored_at, result = entry
        if time.monotonic() - stored_at > RESULT_CACHE_TTL_SECONDS:
            _result_cache.pop(key, None)
            return None
        return result


def _store_cached_result(company: str, result: dict) -> None:
    if RESULT_CACHE_TTL_SECONDS <= 0:
        return
    with _result_cache_lock:
        _result_cache[_cache_key(company)] = (time.monotonic(), result)


def _decode_structured(value):
    if not isinstance(value, str):
        return value
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value


@router.post("/run-agent", dependencies=[Depends(enforce_run_limit)])
def run_agent(request: LeadRequest):

    cached = _get_cached_result(request.company)
    if cached is not None:
        return {**cached, "cached": True}

    result = run_pipeline(request.company)
    _store_cached_result(request.company, result)

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
