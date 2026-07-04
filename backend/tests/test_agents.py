import pytest
class TestKnowledgeAgent:

    def test_get_company_knowledge_returns_context(self):
        from agents.knowledge_agent import get_company_knowledge
        result = get_company_knowledge("Stripe")
        assert isinstance(result, str)
        assert len(result) > 0


class TestResearchAgent:

    def test_research_company_returns_text(self):
        from agents.research_agent import research_company
        result = research_company("OpenAI")
        assert isinstance(result, str)
        assert len(result) > 0


class TestEnrichmentAgent:

    def test_enrich_lead_returns_text(self):
        from agents.enrichment_agent import enrich_lead
        result = enrich_lead("Tesla")
        assert isinstance(result, str)
        assert len(result) > 0


class TestLeadScoringAgent:

    def test_score_lead_returns_score(self):
        from agents.lead_scoring_agent import score_lead
        result = score_lead("Growing fintech company")
        assert isinstance(result, str)
        assert len(result) > 0


class TestPersonalizationAgent:

    def test_generate_personalization_returns_text(self):
        from agents.personalization_agent import generate_personalization
        result = generate_personalization(
            research="Tech company in growth phase",
            knowledge="Sells API products",
            enrichment="Enterprise focus"
        )
        assert isinstance(result, str)
        assert len(result) > 0


class TestEmailAgent:

    def test_generate_email_returns_email(self):
        from agents.email_agent import generate_email
        result = generate_email(
            company_name="Acme Inc",
            personalization="Growth opportunity angle"
        )
        assert isinstance(result, str)
        assert len(result) > 0


class TestReviewerAgent:

    def test_review_outreach_returns_review(self):
        from agents.reviewer_agent import review_outreach
        result = review_outreach(
            research="Fintech research",
            personalization="Personalized angle",
            email="Subject: Hello\n\nBody"
        )
        assert isinstance(result, str)
        assert len(result) > 0
