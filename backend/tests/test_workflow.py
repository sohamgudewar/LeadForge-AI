from unittest.mock import patch

from graph.workflow import MAX_REVISIONS, run_pipeline
from models.outreach import OutreachReview


EXPECTED_KEYS = {
    "company",
    "knowledge",
    "research",
    "enrichment",
    "lead_score",
    "personalization",
    "email",
    "review",
    "revision_count",
}


class TestPipeline:
    def test_run_pipeline_returns_structured_contract(self):
        result = run_pipeline("OpenAI")

        assert set(result) == EXPECTED_KEYS
        assert result["company"] == "OpenAI"
        assert result["research"]["industry"] == "Technology"
        assert result["lead_score"]["score"] == 8
        assert result["email"]["subject"] == "Scale qualified outreach"
        assert result["review"]["approved"] is True
        assert result["revision_count"] == 0

    def test_independent_stages_run_in_parallel(self):
        """Knowledge, research and enrichment only need the company name.

        Each one is made to wait on a barrier that releases only when all
        three are running at the same time; if they ran one after another the
        barrier would time out and the test would fail.
        """
        import threading

        from graph import workflow

        barrier = threading.Barrier(3, timeout=5)
        real_knowledge = workflow.get_company_knowledge
        real_research = workflow.research_company
        real_enrich = workflow.enrich_lead

        def waits(func):
            def wrapper(*args, **kwargs):
                barrier.wait()
                return func(*args, **kwargs)

            return wrapper

        with patch("graph.workflow.get_company_knowledge", waits(real_knowledge)), patch(
            "graph.workflow.research_company", waits(real_research)
        ), patch("graph.workflow.enrich_lead", waits(real_enrich)):
            result = run_pipeline("Acme")

        assert result["personalization"] is not None
        assert result["lead_score"]["score"] == 8

    def test_approved_email_is_not_revised(self):
        with patch("graph.workflow.generate_email", wraps=None) as email_mock:
            from models.outreach import OutreachEmail

            email_mock.return_value = OutreachEmail(
                subject="Subject",
                body="A sufficiently long and useful email body.",
                call_to_action="Can we talk?",
            )
            result = run_pipeline("Acme")

        assert result["revision_count"] == 0
        assert email_mock.call_count == 1

    def test_rejected_email_is_revised_at_most_twice(self):
        rejected = OutreachReview(
            approved=False,
            research_score=8,
            personalization_score=6,
            email_score=4,
            overall_score=5,
            issues=["CTA is vague"],
            revision_instructions=["Use a specific CTA"],
        )

        with patch("graph.workflow.review_outreach", return_value=rejected), patch(
            "graph.workflow.generate_email"
        ) as email_mock:
            from models.outreach import OutreachEmail

            email_mock.return_value = OutreachEmail(
                subject="Subject",
                body="A sufficiently long and useful email body.",
                call_to_action="Are you available Tuesday?",
            )
            result = run_pipeline("Acme")

        assert result["revision_count"] == MAX_REVISIONS
        assert email_mock.call_count == MAX_REVISIONS + 1
        assert result["review"]["approved"] is False
        assert result["review"]["revision_count"] == MAX_REVISIONS
