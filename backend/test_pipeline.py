from agents.research_agent import research_company
from agents.personalization_agent import generate_personalization
from agents.email_agent import generate_email

company = "Stripe"

research = research_company(company)

personalization = generate_personalization(research)

email = generate_email(
    company,
    personalization
)

print(email)
