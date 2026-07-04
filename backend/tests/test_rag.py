import pytest


class TestRetrieveCompanyContext:

    def test_returns_string(self):
        from rag.retriever import retrieve_company_context
        result = retrieve_company_context("test")
        assert isinstance(result, str)

    def test_returns_fallback_when_no_context(self):
        from rag.retriever import retrieve_company_context
        result = retrieve_company_context("nonexistentcompanyxyz")
        assert result == "No company knowledge found."


class TestIngestPdf:

    def test_ingest_fails_on_nonexistent_file(self):
        from rag.ingest import ingest_pdf
        with pytest.raises(Exception):
            ingest_pdf("nonexistent_file.pdf")



