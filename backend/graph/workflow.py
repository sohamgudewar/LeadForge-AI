from langgraph.graph import StateGraph, END

from graph.state import SDRState

from agents.research_agent import research_company
from agents.personalization_agent import generate_personalization
from agents.email_agent import generate_email


def research_node(state: SDRState):

    result = research_company(
        state["company"]
    )

    return {
        "research": result
    }


def personalization_node(state: SDRState):

    result = generate_personalization(
        state["research"]
    )

    return {
        "personalization": result
    }


def email_node(state: SDRState):
    
    result = generate_email(
        state["company"],
        state["personalization"]
    )

    return {
        "email": result
    }


builder = StateGraph(SDRState)

builder.add_node(
    "research",
    research_node
)

builder.add_node(
    "personalization",
    personalization_node
)

builder.add_node(
    "email",
    email_node
)

builder.set_entry_point("research")

builder.add_edge(
    "research",
    "personalization"
)

builder.add_edge(
    "personalization",
    "email"
)

builder.add_edge(
    "email",
    END
)

graph = builder.compile()
