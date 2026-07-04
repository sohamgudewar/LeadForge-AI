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
        assert response.status_code == 200
        assert response.json() == {"error": "Lead not found"}


class TestUploadPdf:

    def test_rejects_non_pdf_files(self, client):
        response = client.post(
            "/upload-pdf",
            files={"file": ("test.txt", b"not a pdf", "text/plain")}
        )
        assert response.status_code == 400
        assert "PDF" in response.json()["detail"]

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

    def test_accepts_valid_company(self, client):
        response = client.post(
            "/run-agent",
            json={"company": "test"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "company" in data
        assert data["company"] == "test"
