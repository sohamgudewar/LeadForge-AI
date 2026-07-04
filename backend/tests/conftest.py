import os
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

import pytest
from unittest.mock import patch
from typing import Generator
from fastapi.testclient import TestClient

from database.models import Base
from database.db import engine, SessionLocal
from main import app


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
    fake_response = type("Response", (), {"content": "Mocked response content"})()
    with patch(
        "langchain_google_genai.ChatGoogleGenerativeAI.invoke",
        return_value=fake_response
    ):
        yield
