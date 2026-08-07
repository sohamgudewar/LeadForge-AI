from agents.structured import invoke_structured
from models.outreach import OutreachEmail, Personalization


def generate_email(
    company_name: str,
    personalization: Personalization,
    revision_instructions: list[str] | None = None
) -> OutreachEmail:

    feedback = revision_instructions or []

    prompt = f"""
    Write a cold outreach email.

    Company:
    {company_name}

    Personalization:
    {personalization.model_dump_json(indent=2)}

    Reviewer revision instructions:
    {feedback}

    Rules:
    - Subject line included
    - Under 120 words
    - Professional
    - Clear CTA

    Incorporate every reviewer instruction when provided.
    """

    return invoke_structured(OutreachEmail, prompt)
