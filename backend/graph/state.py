from typing import TypedDict

from models.outreach import (
    CompanyResearch,
    LeadEnrichment,
    LeadScore,
    OutreachEmail,
    OutreachReview,
    Personalization,
)


class SDRState(TypedDict):

    company: str

    knowledge: str

    research: CompanyResearch | None

    enrichment: LeadEnrichment | None

    lead_score: LeadScore | None

    personalization: Personalization | None

    email: OutreachEmail | None

    review: OutreachReview | None

    revision_count: int
