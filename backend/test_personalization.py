from agents.research_agent import research_company
from agents.personalization_agent import generate_personalization

research = research_company("Stripe")

hook = generate_personalization(research)

print(hook)
