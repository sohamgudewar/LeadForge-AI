from unittest.mock import Mock, patch

from agents.research_agent import research_company
from models.outreach import CompanyResearch, EvidenceClaim, ResearchSource
from research.web_search import search_company


def test_search_returns_empty_list_without_api_key(monkeypatch):
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)
    assert search_company("Acme") == []


def test_search_normalizes_provider_results(monkeypatch):
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {
        "results": [
            {
                "title": "Acme launches a new product",
                "url": "https://example.com/acme-launch",
                "content": "Acme announced its new product today.",
            },
            {
                "title": "Unsafe local result",
                "url": "http://localhost/internal",
                "content": "Must not be exposed.",
            },
        ]
    }

    with patch("research.web_search.httpx.post", return_value=response):
        sources = search_company("Acme")

    assert len(sources) == 1
    assert sources[0].source_id == "S1"
    assert sources[0].url == "https://example.com/acme-launch"


def test_research_discards_citations_not_returned_by_search():
    source = ResearchSource(
        source_id="S1",
        title="Acme product announcement",
        url="https://example.com/acme",
        snippet="Acme launched a product.",
    )
    model_result = CompanyResearch(
        industry="Technology",
        summary="A technology company.",
        business_challenges=["Scaling"],
        sales_opportunities=["Automation"],
        evidence=[
            EvidenceClaim(claim="Acme launched a product.", source_id="S1"),
            EvidenceClaim(claim="An unsupported claim.", source_id="S5"),
        ],
    )

    with patch("agents.research_agent.search_company", return_value=[source]), patch(
        "agents.research_agent.invoke_structured", return_value=model_result
    ):
        result = research_company("Acme")

    assert [claim.source_id for claim in result.evidence] == ["S1"]
    assert result.sources == [source]
