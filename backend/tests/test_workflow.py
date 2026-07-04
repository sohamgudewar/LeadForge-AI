import pytest
from graph.state import SDRState


class TestSDRState:

    def test_has_all_required_keys(self):
        state: SDRState = {
            "company": "",
            "knowledge": "",
            "research": "",
            "enrichment": "",
            "lead_score": "",
            "personalization": "",
            "email": "",
            "review": "",
        }
        assert set(state.keys()) == {
            "company", "knowledge", "research", "enrichment",
            "lead_score", "personalization", "email", "review"
        }

    def test_company_is_required(self):
        state: SDRState = {
            "company": "Stripe",
            "knowledge": "",
            "research": "",
            "enrichment": "",
            "lead_score": "",
            "personalization": "",
            "email": "",
            "review": "",
        }
        assert state["company"] == "Stripe"

    def test_optional_fields_default_to_empty_string(self):
        state: SDRState = {
            "company": "Acme",
            "knowledge": "",
            "research": "",
            "enrichment": "",
            "lead_score": "",
            "personalization": "",
            "email": "",
            "review": "",
        }
        for key in ("knowledge", "research", "enrichment",
                     "lead_score", "personalization", "email", "review"):
            assert state[key] == ""


class TestPipeline:

    def test_run_pipeline_returns_all_keys(self):
        from graph.workflow import run_pipeline
        result = run_pipeline("test")
        expected_keys = {
            "company", "knowledge", "research", "enrichment",
            "lead_score", "personalization", "email", "review"
        }
        assert set(result.keys()) == expected_keys

    def test_run_pipeline_company_in_result(self):
        from graph.workflow import run_pipeline
        result = run_pipeline("OpenAI")
        assert result["company"] == "OpenAI"

    def test_run_pipeline_populates_fields(self):
        from graph.workflow import run_pipeline
        result = run_pipeline("Anthropic")
        assert result["research"]
        assert result["enrichment"]
        assert result["lead_score"]
        assert result["personalization"]
        assert result["email"]
        assert result["review"]
