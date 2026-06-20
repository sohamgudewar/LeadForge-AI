from database.db import SessionLocal
from database.models import Lead


def save_lead(data):

    db = SessionLocal()

    lead = Lead(
        company=data["company"],
        knowledge=data["knowledge"],
        research=data["research"],
        enrichment=data["enrichment"],
        lead_score=data["lead_score"],
        personalization=data["personalization"],
        email=data["email"],
        review=data["review"]
    )

    db.add(lead)

    db.commit()

    db.close()


def get_leads():

    db = SessionLocal()

    leads = db.query(Lead).all()

    db.close()

    return leads


def get_lead_by_id(lead_id):

    db = SessionLocal()

    lead = db.query(
        Lead
    ).filter(
        Lead.id == lead_id
    ).first()

    db.close()

    return lead
