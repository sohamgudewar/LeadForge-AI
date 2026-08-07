from unittest.mock import Mock, patch

import pytest

from agents.structured import (
    MAX_STRUCTURED_ATTEMPTS,
    StructuredOutputError,
    invoke_structured,
)
from models.outreach import LeadScore


def test_retries_malformed_output_then_returns_valid_model():
    runnable = Mock()
    runnable.invoke.side_effect = [
        {"score": 99},
        {"score": 8, "reasons": ["Strong fit"]},
    ]
    llm = Mock()
    llm.with_structured_output.return_value = runnable

    with patch("agents.structured.get_llm", return_value=llm):
        result = invoke_structured(LeadScore, "score this lead")

    assert result.score == 8
    assert runnable.invoke.call_count == 2


def test_raises_clear_error_after_retry_limit():
    runnable = Mock()
    runnable.invoke.return_value = {"score": 99}
    llm = Mock()
    llm.with_structured_output.return_value = runnable

    with patch("agents.structured.get_llm", return_value=llm), pytest.raises(
        StructuredOutputError, match="LeadScore"
    ):
        invoke_structured(LeadScore, "score this lead")

    assert runnable.invoke.call_count == MAX_STRUCTURED_ATTEMPTS
