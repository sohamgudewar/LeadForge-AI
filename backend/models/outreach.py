from typing import Literal

from pydantic import BaseModel, Field


class CompanyResearch(BaseModel):
    industry: str
    summary: str
    business_challenges: list[str] = Field(min_length=1, max_length=5)
    sales_opportunities: list[str] = Field(min_length=1, max_length=5)
    evidence: list["EvidenceClaim"] = Field(default_factory=list, max_length=8)
    sources: list["ResearchSource"] = Field(default_factory=list, max_length=5)


class EvidenceClaim(BaseModel):
    claim: str = Field(min_length=3, max_length=500)
    source_id: str = Field(pattern=r"^S[1-5]$")


class ResearchSource(BaseModel):
    source_id: str = Field(pattern=r"^S[1-5]$")
    title: str = Field(min_length=1, max_length=300)
    url: str = Field(pattern=r"^https?://")
    snippet: str = Field(default="", max_length=1000)


class LeadEnrichment(BaseModel):
    estimated_company_size: str
    target_buyers: list[str] = Field(min_length=1, max_length=5)
    relevant_departments: list[str] = Field(min_length=1, max_length=5)
    decision_makers: list[str] = Field(min_length=1, max_length=5)
    outreach_priority: Literal["low", "medium", "high"]


class LeadScore(BaseModel):
    score: int = Field(ge=1, le=10)
    reasons: list[str] = Field(min_length=1, max_length=4)


class Personalization(BaseModel):
    angle: str = Field(min_length=10, max_length=500)


class OutreachEmail(BaseModel):
    subject: str = Field(min_length=3, max_length=120)
    body: str = Field(min_length=20, max_length=1500)
    call_to_action: str = Field(min_length=3, max_length=300)


class OutreachReview(BaseModel):
    approved: bool
    research_score: int = Field(ge=1, le=10)
    personalization_score: int = Field(ge=1, le=10)
    email_score: int = Field(ge=1, le=10)
    overall_score: int = Field(ge=1, le=10)
    strengths: list[str] = Field(default_factory=list, max_length=5)
    issues: list[str] = Field(default_factory=list, max_length=5)
    revision_instructions: list[str] = Field(default_factory=list, max_length=5)
