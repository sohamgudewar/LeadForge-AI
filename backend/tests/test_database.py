import pytest
from database.crud import save_lead, get_leads, get_lead_by_id
from database.models import Lead


class TestSaveLead:

    def test_saves_lead_with_all_fields(self, sample_lead_data):
        save_lead(sample_lead_data)

        leads = get_leads()
        assert len(leads) == 1
        lead = leads[0]
        assert lead.company == "TestCorp"
        assert lead.knowledge == "Knowledge base info"
        assert lead.research == "Industry research"
        assert lead.enrichment == "Enrichment data"
        assert lead.lead_score == "Score: 7/10"
        assert lead.personalization == "Personalized angle"
        assert lead.email == "Subject: Hello\n\nEmail body here"
        assert lead.review == "Quality review"

    def test_saves_multiple_leads(self, sample_lead_data):
        data2 = {**sample_lead_data, "company": "Corp2"}
        data3 = {**sample_lead_data, "company": "Corp3"}

        save_lead(sample_lead_data)
        save_lead(data2)
        save_lead(data3)

        leads = get_leads()
        assert len(leads) == 3

    def test_id_is_auto_incremented(self, sample_lead_data):
        save_lead(sample_lead_data)
        save_lead({**sample_lead_data, "company": "Another"})

        leads = get_leads()
        assert leads[0].id == 1
        assert leads[1].id == 2


class TestGetLeads:

    def test_returns_empty_list_when_no_leads(self):
        leads = get_leads()
        assert leads == []

    def test_returns_all_leads(self, db_session):
        db_session.add_all([
            Lead(company="A", knowledge="", research="",
                 enrichment="", lead_score="", personalization="",
                 email="", review=""),
            Lead(company="B", knowledge="", research="",
                 enrichment="", lead_score="", personalization="",
                 email="", review=""),
        ])
        db_session.commit()

        leads = get_leads()
        assert len(leads) == 2


class TestGetLeadById:

    def test_returns_lead_when_exists(self, sample_lead):
        lead = get_lead_by_id(sample_lead.id)
        assert lead is not None
        assert lead.company == "TestCorp"

    def test_returns_none_when_not_found(self):
        lead = get_lead_by_id(999)
        assert lead is None

    def test_returns_correct_lead(self, sample_lead_data):
        save_lead(sample_lead_data)
        save_lead({**sample_lead_data, "company": "Other"})

        lead = get_lead_by_id(2)
        assert lead.company == "Other"
