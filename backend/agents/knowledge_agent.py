def get_company_knowledge(company: str):
    
    company = company.lower()

    knowledge_base = {

        "slack": """
Slack is owned by Salesforce.

Main focus:
Enterprise communication.

Competitors:
Microsoft Teams
Google Workspace

Key strength:
Enterprise collaboration.
""",

        "openai": """
OpenAI develops frontier AI models.

Products:
ChatGPT
GPT API

Focus:
Enterprise AI adoption.
"""
    }

    return knowledge_base.get(
        company,
        "No internal company knowledge available."
    )
