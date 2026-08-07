from agents.structured import invoke_structured
from models.outreach import (
    CompanyResearch,
    OutreachEmail,
    OutreachReview,
    Personalization,
)


def review_outreach(
    research: CompanyResearch,
    personalization: Personalization,
    email: OutreachEmail
) -> OutreachReview:

    prompt = f"""
You are a senior SDR manager.

Review the following outreach package.

Research:
{research.model_dump_json(indent=2)}

Personalization:
{personalization.model_dump_json(indent=2)}

Email:
{email.model_dump_json(indent=2)}

Evaluate:

1. Research Quality (1-10)
2. Personalization Quality (1-10)
3. Email Quality (1-10)
4. Overall SDR Readiness Score

Approve only if the email is relevant, concise, professional, has a clear CTA,
and does not make unsupported claims. If rejected, provide concrete revision
instructions.

Keep response concise.
"""

    return invoke_structured(OutreachReview, prompt)
