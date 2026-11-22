import os
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["SKIP_WARMUP"] = "1"

import pytest
from contextlib import ExitStack
from unittest.mock import patch
from typing import Generator
from fastapi.testclient import TestClient

from database.models import Base
from database.db import engine, SessionLocal
from main import app
from models.outreach import (
    CompanyResearch,
    LeadEnrichment,
    LeadScore,
    OutreachEmail,
    OutreachReview,
    Personalization,
)


@pytest.fixture(autouse=True)
def _clear_result_cache():
    from api import routes

    routes._result_cache.clear()
    yield
    routes._result_cache.clear()


@pytest.fixture(autouse=True, scope="function")
def _setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def client() -> Generator:
    with TestClient(app) as c:
        yield c


@pytest.fixture
def sample_lead(db_session):
    from database.models import Lead
    lead = Lead(
        company="TestCorp",
        knowledge="Test knowledge",
        research="Test research",
        enrichment="Test enrichment",
        lead_score="Score: 8/10",
        personalization="Test personalization",
        email="Subject: Test\n\nBody",
        review="Test review"
    )
    db_session.add(lead)
    db_session.commit()
    db_session.refresh(lead)
    return lead


@pytest.fixture
def sample_lead_data():
    return {
        "company": "TestCorp",
        "knowledge": "Knowledge base info",
        "research": "Industry research",
        "enrichment": "Enrichment data",
        "lead_score": "Score: 7/10",
        "personalization": "Personalized angle",
        "email": "Subject: Hello\n\nEmail body here",
        "review": "Quality review"
    }


@pytest.fixture(autouse=True)
def _mock_llm():
    def structured_result(schema, _prompt):
        values = {
            CompanyResearch: CompanyResearch(
                industry="Technology",
                summary="A growing technology company.",
                business_challenges=["Scaling sales operations"],
                sales_opportunities=["Automate lead qualification"],
            ),
            LeadEnrichment: LeadEnrichment(
                estimated_company_size="201-500 employees",
                target_buyers=["VP Sales"],
                relevant_departments=["Sales"],
                decision_makers=["Chief Revenue Officer"],
                outreach_priority="high",
            ),
            LeadScore: LeadScore(score=8, reasons=["Strong product fit"]),
            Personalization: Personalization(
                angle="Help the revenue team scale qualified outreach efficiently."
            ),
            OutreachEmail: OutreachEmail(
                subject="Scale qualified outreach",
                body="Your revenue team may benefit from a more efficient qualification workflow.",
                call_to_action="Open to a short conversation next week?",
            ),
            OutreachReview: OutreachReview(
                approved=True,
                research_score=8,
                personalization_score=8,
                email_score=8,
                overall_score=8,
                strengths=["Concise and relevant"],
            ),
        }
        return values[schema]

    targets = [
        "agents.research_agent.invoke_structured",
        "agents.enrichment_agent.invoke_structured",
        "agents.lead_scoring_agent.invoke_structured",
        "agents.personalization_agent.invoke_structured",
        "agents.email_agent.invoke_structured",
        "agents.reviewer_agent.invoke_structured",
    ]
    with ExitStack() as stack:
        for target in targets:
            stack.enter_context(patch(target, side_effect=structured_result))
        yield


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    from api.rate_limit import limiter
    limiter.reset()
    yield
    limiter.reset()
