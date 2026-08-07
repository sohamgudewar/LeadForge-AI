import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

from pydantic import BaseModel, Field

from config import MODEL_NAME
from evaluation.metrics import CaseResult, EvaluationCase, evaluate_result
from graph.workflow import run_pipeline

EVALUATION_DIR = Path(__file__).resolve().parent
DEFAULT_CASES_PATH = EVALUATION_DIR / "cases.json"
DEFAULT_RESULTS_DIR = EVALUATION_DIR / "results"


class EvaluationSummary(BaseModel):
    run_at: str
    model: str
    total_cases: int
    completed_cases: int
    passed_cases: int
    pass_rate: float = Field(ge=0, le=1)
    schema_valid_rate: float = Field(ge=0, le=1)
    industry_match_rate: float = Field(ge=0, le=1)
    citation_integrity_rate: float = Field(ge=0, le=1)
    web_evidence_coverage: float = Field(ge=0, le=1)
    email_constraint_rate: float = Field(ge=0, le=1)
    reviewer_approval_rate: float = Field(ge=0, le=1)
    average_latency_seconds: float = Field(ge=0)
    average_revisions: float = Field(ge=0)
    failed_runs: int
    results: list[CaseResult]


def load_cases(path: Path = DEFAULT_CASES_PATH) -> list[EvaluationCase]:
    raw_cases = json.loads(path.read_text(encoding="utf-8"))
    return [EvaluationCase.model_validate(case) for case in raw_cases]


def _rate(results: list[CaseResult], field: str) -> float:
    if not results:
        return 0.0
    return round(sum(bool(getattr(result, field)) for result in results) / len(results), 3)


def build_summary(
    cases: list[EvaluationCase],
    results: list[CaseResult],
    failed_runs: int,
) -> EvaluationSummary:
    completed = len(results)
    return EvaluationSummary(
        run_at=datetime.now(timezone.utc).isoformat(),
        model=MODEL_NAME,
        total_cases=len(cases),
        completed_cases=completed,
        passed_cases=sum(result.passed for result in results),
        pass_rate=round(
            sum(result.passed for result in results) / len(cases), 3
        ) if cases else 0.0,
        schema_valid_rate=_rate(results, "schema_valid"),
        industry_match_rate=_rate(results, "industry_match"),
        citation_integrity_rate=_rate(results, "citations_valid"),
        web_evidence_coverage=_rate(results, "has_web_evidence"),
        email_constraint_rate=_rate(results, "email_under_120_words"),
        reviewer_approval_rate=_rate(results, "reviewer_approved"),
        average_latency_seconds=round(
            sum(result.latency_seconds for result in results) / completed, 3
        ) if completed else 0.0,
        average_revisions=round(
            sum(result.revision_count for result in results) / completed, 3
        ) if completed else 0.0,
        failed_runs=failed_runs,
        results=results,
    )


def run_evaluation(cases: list[EvaluationCase]) -> EvaluationSummary:
    results = []
    failed_runs = 0
    for index, case in enumerate(cases, start=1):
        print(f"[{index}/{len(cases)}] Evaluating {case.company}...")
        started = perf_counter()
        try:
            pipeline_result = run_pipeline(case.company)
            results.append(
                evaluate_result(case, pipeline_result, perf_counter() - started)
            )
        except Exception as exc:
            failed_runs += 1
            print(f"  Failed: {type(exc).__name__}: {exc}")
    return build_summary(cases, results, failed_runs)


def save_summary(summary: EvaluationSummary, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(summary.model_dump_json(indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate the LeadForge AI pipeline")
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES_PATH)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    cases = load_cases(args.cases)
    if args.limit is not None:
        if args.limit < 1:
            parser.error("--limit must be at least 1")
        cases = cases[:args.limit]

    summary = run_evaluation(cases)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_path = args.output or DEFAULT_RESULTS_DIR / f"evaluation-{timestamp}.json"
    save_summary(summary, output_path)

    print(f"\nPass rate: {summary.pass_rate:.1%}")
    print(f"Schema validity: {summary.schema_valid_rate:.1%}")
    print(f"Citation integrity: {summary.citation_integrity_rate:.1%}")
    print(f"Average latency: {summary.average_latency_seconds:.2f}s")
    print(f"Report: {output_path}")


if __name__ == "__main__":
    main()
