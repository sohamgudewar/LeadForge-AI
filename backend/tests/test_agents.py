from agents.email_agent import generate_email
from agents.enrichment_agent import enrich_lead
from agents.lead_scoring_agent import score_lead
from agents.personalization_agent import generate_personalization
from agents.research_agent import research_company
from agents.reviewer_agent import review_outreach
from models.outreach import (
    CompanyResearch,
    LeadEnrichment,
    LeadScore,
    OutreachEmail,
    OutreachReview,
    Personalization,
)


def test_agents_return_validated_models():
    research = research_company("OpenAI")
    enrichment = enrich_lead("OpenAI")
    score = score_lead(research)
    personalization = generate_personalization(research, "Knowledge", enrichment)
    email = generate_email("OpenAI", personalization)
    review = review_outreach(research, personalization, email)

    assert isinstance(research, CompanyResearch)
    assert isinstance(enrichment, LeadEnrichment)
    assert isinstance(score, LeadScore)
    assert isinstance(personalization, Personalization)
    assert isinstance(email, OutreachEmail)
    assert isinstance(review, OutreachReview)
    assert 1 <= score.score <= 10


def test_email_agent_accepts_revision_instructions():
    result = generate_email(
        "Acme",
        Personalization(angle="Help Acme qualify leads more consistently."),
        ["Make the CTA specific"],
    )
    assert isinstance(result, OutreachEmail)
