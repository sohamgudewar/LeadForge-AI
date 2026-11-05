"""Tests for rate limiting, duplicate-free ingestion and multi-query retrieval."""

from unittest.mock import patch
from uuid import uuid4

import pytest
from fastapi import HTTPException
from langchain_core.documents import Document

from api.rate_limit import SlidingWindowLimiter, limiter


class TestSlidingWindowLimiter:

    def test_blocks_client_after_limit_and_sets_retry_after(self):
        rl = SlidingWindowLimiter(per_client=2, global_limit=100, window=60)
        rl.check("1.1.1.1", now=0)
        rl.check("1.1.1.1", now=10)
        with pytest.raises(HTTPException) as exc:
            rl.check("1.1.1.1", now=20)
        assert exc.value.status_code == 429
        assert exc.value.headers["Retry-After"] == "40"

    def test_other_clients_are_not_affected(self):
        rl = SlidingWindowLimiter(per_client=1, global_limit=100, window=60)
        rl.check("1.1.1.1", now=0)
        rl.check("2.2.2.2", now=0)

    def test_window_slides(self):
        rl = SlidingWindowLimiter(per_client=1, global_limit=100, window=60)
        rl.check("1.1.1.1", now=0)
        rl.check("1.1.1.1", now=61)

    def test_global_cap_applies_across_clients(self):
        rl = SlidingWindowLimiter(per_client=10, global_limit=2, window=60)
        rl.check("a", now=0)
        rl.check("b", now=0)
        with pytest.raises(HTTPException) as exc:
            rl.check("c", now=0)
        assert exc.value.status_code == 429

    def test_rejected_calls_do_not_consume_quota(self):
        rl = SlidingWindowLimiter(per_client=1, global_limit=100, window=60)
        rl.check("a", now=0)
        for _ in range(5):
            with pytest.raises(HTTPException):
                rl.check("a", now=1)
        rl.check("a", now=60.5)


class TestRunAgentRateLimit:

    def test_run_agent_returns_429_when_limit_reached(self, client):
        with patch.object(limiter, "per_client", 1), \
                patch("api.routes.run_pipeline", return_value={"company": "Acme"}), \
                patch("api.routes.save_lead"):
            assert client.post("/run-agent", json={"company": "Acme"}).status_code == 200
            response = client.post("/run-agent", json={"company": "Acme"})
        assert response.status_code == 429
        assert "Retry-After" in response.headers

    def test_read_endpoints_are_not_rate_limited(self, client):
        with patch.object(limiter, "per_client", 1):
            for _ in range(3):
                assert client.get("/leads").status_code == 200


class TestIngestDeduplication:

    def test_reingesting_same_pdf_does_not_duplicate_chunks(self):
        from rag.ingest import ingest_pdf
        from rag.retriever import _get_vectorstore

        company = f"dedupe-test-{uuid4().hex[:8]}"
        pages = [
            Document(page_content="Acme sells industrial sensors to factories.", metadata={}),
            Document(page_content="Acme plans to expand into Southeast Asia.", metadata={}),
        ]
        vs = _get_vectorstore()
        try:
            with patch("rag.ingest.PyPDFLoader") as loader:
                loader.return_value.load.side_effect = lambda: [
                    Document(page_content=p.page_content, metadata={}) for p in pages
                ]
                ingest_pdf("ignored.pdf", company_name=company)
                ingest_pdf("ignored.pdf", company_name=company)

            stored = vs.get(where={"company": company})
            assert len(stored["ids"]) == 2
        finally:
            vs.delete(where={"company": company})

    def test_company_key_is_normalized(self):
        from rag.retriever import normalize_company
        assert normalize_company("  Acme   Corp ") == "acme corp"


class TestMultiQueryRetrieval:

    def test_runs_one_search_per_query_and_deduplicates(self):
        from rag import retriever

        shared = Document(page_content="shared chunk")
        calls = []

        class FakeStore:
            def similarity_search(self, query, k, filter):
                calls.append((query, k, filter))
                return [shared, Document(page_content=f"unique for {query}")]

        with patch.object(retriever, "_get_vectorstore", return_value=FakeStore()):
            context = retriever.retrieve_company_context("Acme  Corp")

        assert len(calls) == len(retriever.RETRIEVAL_QUERIES)
        assert all(f == {"company": "acme corp"} for _, _, f in calls)
        assert context.count("shared chunk") == 1
        assert len(context.split("\n\n")) <= retriever.MAX_CONTEXT_CHUNKS
