import pytest
import os
from pathlib import Path
import tempfile


class TestRetrieveCompanyContext:

    def test_onnx_cache_uses_writable_temp_directory_by_default(self):
        from rag.retriever import MODEL_CACHE_PATH, ONNXMiniLM_L6_V2

        expected = Path(
            os.getenv(
                "CHROMA_MODEL_CACHE_PATH",
                str(
                    Path(tempfile.gettempdir())
                    / "chroma"
                    / "onnx_models"
                    / ONNXMiniLM_L6_V2.MODEL_NAME
                ),
            )
        )
        assert MODEL_CACHE_PATH == expected
        assert ONNXMiniLM_L6_V2.DOWNLOAD_PATH == expected

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

