from agents.followup_agent import generate_followup

result = generate_followup(
    "Slack",
    """
Hi Team,

I wanted to reach out regarding your AI initiatives.

Would love to schedule a short call.

Best,
Soham
"""
)

print(result)
