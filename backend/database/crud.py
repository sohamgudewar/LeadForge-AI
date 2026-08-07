import json

from database.db import SessionLocal
from database.models import Lead


def _as_text(value):
    if isinstance(value, (dict, list)):
        return json.dumps(value)
    return value


def save_lead(data):
    db = SessionLocal()
    try:
        lead = Lead(
            company=data["company"],
            knowledge=data["knowledge"],
            research=_as_text(data["research"]),
            enrichment=_as_text(data["enrichment"]),
            lead_score=_as_text(data["lead_score"]),
            personalization=_as_text(data["personalization"]),
            email=_as_text(data["email"]),
            review=_as_text(data["review"])
        )
        db.add(lead)
        db.commit()
        db.refresh(lead)
        return lead
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_leads():
    db = SessionLocal()
    try:
        return db.query(Lead).all()
    finally:
        db.close()


def get_lead_by_id(lead_id):
    db = SessionLocal()
    try:
        return db.query(Lead).filter(Lead.id == lead_id).first()
    finally:
        db.close()
