from pathlib import Path
from unittest.mock import patch

from evaluation.metrics import EvaluationCase, evaluate_result
from evaluation.run import build_summary, load_cases, run_evaluation, save_summary


def valid_pipeline_result():
    return {
        "company": "Acme",
        "knowledge": "Internal context",
        "research": {
            "industry": "Payment technology",
            "summary": "Acme provides payment software.",
            "business_challenges": ["Scaling operations"],
            "sales_opportunities": ["Automated qualification"],
            "evidence": [
                {"claim": "Acme launched a product.", "source_id": "S1"}
            ],
            "sources": [
                {
                    "source_id": "S1",
                    "title": "Acme announcement",
                    "url": "https://example.com/acme",
                    "snippet": "Acme launched a product.",
                }
            ],
        },
        "enrichment": {
            "estimated_company_size": "201-500 employees",
            "target_buyers": ["VP Sales"],
            "relevant_departments": ["Sales"],
            "decision_makers": ["CRO"],
            "outreach_priority": "high",
        },
        "lead_score": {"score": 8, "reasons": ["Strong fit"]},
        "personalization": {"angle": "Help Acme scale its sales workflow."},
        "email": {
            "subject": "Acme sales workflow",
            "body": "Acme can qualify leads more consistently with a focused workflow.",
            "call_to_action": "Could we discuss this Tuesday?",
        },
        "review": {
            "approved": True,
            "research_score": 8,
            "personalization_score": 8,
            "email_score": 8,
            "overall_score": 8,
            "strengths": ["Concise"],
            "issues": [],
            "revision_instructions": [],
        },
        "revision_count": 0,
    }


def test_loads_ten_versioned_cases():
    cases = load_cases()
    assert len(cases) == 10
    assert all(case.industry_keywords for case in cases)


def test_valid_result_passes_all_required_metrics():
    case = EvaluationCase(
        company="Acme",
        industry_keywords=["payment"],
        required_email_terms=["Acme"],
    )
    result = evaluate_result(case, valid_pipeline_result(), 1.2345)

    assert result.passed is True
    assert result.schema_valid is True
    assert result.citations_valid is True
    assert result.has_web_evidence is True
    assert result.latency_seconds == 1.234


def test_unknown_citation_fails_integrity_metric():
    case = EvaluationCase(company="Acme", industry_keywords=["payment"])
    pipeline_result = valid_pipeline_result()
    pipeline_result["research"]["evidence"][0]["source_id"] = "S5"

    result = evaluate_result(case, pipeline_result, 1.0)

    assert result.passed is False
    assert result.citations_valid is False
    assert "Evidence contained an unknown source ID" in result.errors


def test_failed_pipeline_run_reduces_overall_pass_rate():
    cases = [
        EvaluationCase(company="Acme", industry_keywords=["payment"]),
        EvaluationCase(company="Broken", industry_keywords=["software"]),
    ]
    with patch(
        "evaluation.run.run_pipeline",
        side_effect=[valid_pipeline_result(), RuntimeError("model unavailable")],
    ):
        summary = run_evaluation(cases)

    assert summary.completed_cases == 1
    assert summary.failed_runs == 1
    assert summary.pass_rate == 0.5


def test_summary_can_be_saved_as_json(tmp_path: Path):
    case = EvaluationCase(company="Acme", industry_keywords=["payment"])
    case_result = evaluate_result(case, valid_pipeline_result(), 1.0)
    summary = build_summary([case], [case_result], failed_runs=0)
    output = tmp_path / "report.json"

    save_summary(summary, output)

    assert output.exists()
    assert '"schema_valid_rate": 1.0' in output.read_text(encoding="utf-8")
