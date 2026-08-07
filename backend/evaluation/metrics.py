from pydantic import BaseModel, Field, ValidationError

from models.outreach import (
    CompanyResearch,
    LeadEnrichment,
    LeadScore,
    OutreachEmail,
    OutreachReview,
    Personalization,
)


class EvaluationCase(BaseModel):
    company: str
    industry_keywords: list[str] = Field(min_length=1)
    required_email_terms: list[str] = Field(default_factory=list)


class CaseResult(BaseModel):
    company: str
    passed: bool
    schema_valid: bool
    industry_match: bool
    citations_valid: bool
    has_web_evidence: bool
    email_under_120_words: bool
    required_email_terms_present: bool
    reviewer_approved: bool
    revision_count: int = Field(ge=0)
    latency_seconds: float = Field(ge=0)
    errors: list[str] = Field(default_factory=list)


def _validate_contract(result: dict) -> tuple[bool, list[str]]:
    errors = []
    validators = {
        "research": CompanyResearch,
        "enrichment": LeadEnrichment,
        "lead_score": LeadScore,
        "personalization": Personalization,
        "email": OutreachEmail,
        "review": OutreachReview,
    }
    for field, schema in validators.items():
        try:
            schema.model_validate(result.get(field))
        except ValidationError as exc:
            errors.append(f"Invalid {field}: {exc.error_count()} schema error(s)")
    return not errors, errors


def evaluate_result(
    case: EvaluationCase,
    result: dict,
    latency_seconds: float,
) -> CaseResult:
    schema_valid, errors = _validate_contract(result)
    research = result.get("research") if isinstance(result.get("research"), dict) else {}
    email = result.get("email") if isinstance(result.get("email"), dict) else {}
    review = result.get("review") if isinstance(result.get("review"), dict) else {}

    industry = str(research.get("industry", "")).lower()
    industry_match = any(term.lower() in industry for term in case.industry_keywords)

    sources = research.get("sources", []) if isinstance(research.get("sources", []), list) else []
    source_ids = {
        source.get("source_id") for source in sources if isinstance(source, dict)
    }
    evidence = research.get("evidence", []) if isinstance(research.get("evidence", []), list) else []
    citations_valid = all(
        isinstance(claim, dict) and claim.get("source_id") in source_ids
        for claim in evidence
    )

    email_text = " ".join(
        str(email.get(field, "")) for field in ("subject", "body", "call_to_action")
    )
    email_under_limit = len(email_text.split()) <= 120
    required_terms_present = all(
        term.lower() in email_text.lower() for term in case.required_email_terms
    )

    checks = [
        schema_valid,
        industry_match,
        citations_valid,
        email_under_limit,
        required_terms_present,
    ]
    if not industry_match:
        errors.append("Industry did not match an expected keyword")
    if not citations_valid:
        errors.append("Evidence contained an unknown source ID")
    if not email_under_limit:
        errors.append("Email exceeded 120 words")
    if not required_terms_present:
        errors.append("Email omitted a required company term")

    return CaseResult(
        company=case.company,
        passed=all(checks),
        schema_valid=schema_valid,
        industry_match=industry_match,
        citations_valid=citations_valid,
        has_web_evidence=bool(evidence),
        email_under_120_words=email_under_limit,
        required_email_terms_present=required_terms_present,
        reviewer_approved=bool(review.get("approved")),
        revision_count=int(result.get("revision_count", 0)),
        latency_seconds=round(latency_seconds, 3),
        errors=errors,
    )
