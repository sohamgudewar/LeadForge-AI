import pytest


class TestHealth:

    def test_health_endpoint_returns_ok(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestGetLeads:

    def test_returns_empty_list(self, client):
        response = client.get("/leads")
        assert response.status_code == 200
        assert response.json() == []

    def test_returns_all_leads(self, client, sample_lead):
        response = client.get("/leads")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["company"] == "TestCorp"
        assert data[0]["id"] == sample_lead.id


class TestGetLeadById:

    def test_returns_lead_when_exists(self, client, sample_lead):
        response = client.get(f"/lead/{sample_lead.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["company"] == "TestCorp"
        assert data["research"] == "Test research"
        assert data["email"] == "Subject: Test\n\nBody"

    def test_returns_404_when_not_found(self, client):
        response = client.get("/lead/999")
        assert response.status_code == 404
        assert response.json() == {"detail": "Lead not found"}


class TestUploadPdf:

    def test_rejects_non_pdf_files(self, client):
        response = client.post(
            "/upload-pdf",
            files={"file": ("test.txt", b"not a pdf", "text/plain")}
        )
        assert response.status_code == 400
        assert "PDF" in response.json()["detail"]

    def test_rejects_fake_pdf_content(self, client):
        response = client.post(
            "/upload-pdf",
            files={"file": ("test.pdf", b"not a pdf", "application/pdf")}
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "File content is not a valid PDF"

    def test_rejects_empty_filename(self, client):
        response = client.post(
            "/upload-pdf",
            files={"file": ("", b"", "application/pdf")}
        )
        assert response.status_code == 422


class TestRunAgent:

    def test_rejects_empty_body(self, client):
        response = client.post(
            "/run-agent",
            json={}
        )
        assert response.status_code == 422

    def test_rejects_invalid_json(self, client):
        response = client.post(
            "/run-agent",
            data="not json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422

    @pytest.mark.parametrize("company", ["", "   ", "a"])
    def test_rejects_invalid_company(self, client, company):
        response = client.post("/run-agent", json={"company": company})
        assert response.status_code == 422

    def test_normalizes_company_whitespace(self, client):
        response = client.post(
            "/run-agent",
            json={"company": "  Acme    Corporation  "}
        )
        assert response.status_code == 200
        assert response.json()["company"] == "Acme Corporation"

    def test_repeat_company_is_served_from_cache(self, client):
        from unittest.mock import patch
        from graph.workflow import run_pipeline as real_pipeline

        with patch("api.routes.run_pipeline", wraps=real_pipeline) as pipeline:
            first = client.post("/run-agent", json={"company": "Acme"})
            second = client.post("/run-agent", json={"company": "  acme "})

        assert first.status_code == second.status_code == 200
        assert pipeline.call_count == 1
        assert "cached" not in first.json()
        assert second.json()["cached"] is True
        assert second.json()["email"] == first.json()["email"]

    def test_model_failure_returns_clear_error(self, client):
        from unittest.mock import patch

        with patch("api.routes.run_pipeline", side_effect=TimeoutError("model timed out")):
            response = client.post("/run-agent", json={"company": "Acme"})

        assert response.status_code == 502
        assert "model timed out" in response.json()["detail"]

    def test_accepts_valid_company(self, client):
        response = client.post(
            "/run-agent",
            json={"company": "test"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "company" in data
        assert data["company"] == "test"
        assert data["lead_score"]["score"] == 8
        assert data["email"]["subject"] == "Scale qualified outreach"
        assert data["review"]["approved"] is True
        assert data["revision_count"] == 0
