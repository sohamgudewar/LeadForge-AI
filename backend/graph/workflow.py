from langgraph.graph import StateGraph, END

from graph.state import SDRState

from agents.knowledge_agent import get_company_knowledge
from agents.research_agent import research_company
from agents.enrichment_agent import enrich_lead
from agents.lead_scoring_agent import score_lead
from agents.personalization_agent import generate_personalization
from agents.email_agent import generate_email
from agents.reviewer_agent import review_outreach


def knowledge_node(state: SDRState):

    result = get_company_knowledge(
        state["company"]
    )

    return {
        "knowledge": result
    }


def research_node(state: SDRState):

    result = research_company(
        state["company"]
    )

    return {
        "research": result
    }


def enrichment_node(state: SDRState):

    result = enrich_lead(
        state["company"]
    )

    return {
        "enrichment": result
    }


def scoring_node(state: SDRState):

    result = score_lead(
        state["research"]
    )

    return {
        "lead_score": result
    }


def personalization_node(state: SDRState):

    result = generate_personalization(
        state["research"],
        state["knowledge"],
        state["enrichment"]
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


def review_node(state: SDRState):

    result = review_outreach(
        state["research"],
        state["personalization"],
        state["email"]
    )

    return {
        "review": result
    }


builder = StateGraph(SDRState)

builder.add_node(
    "knowledge",
    knowledge_node
)

builder.add_node(
    "research",
    research_node
)

builder.add_node(
    "enrichment",
    enrichment_node
)

builder.add_node(
    "scoring",
    scoring_node
)

builder.add_node(
    "personalization",
    personalization_node
)

builder.add_node(
    "email",
    email_node
)

builder.add_node(
    "review",
    review_node
)

builder.set_entry_point(
    "knowledge"
)

builder.add_edge(
    "knowledge",
    "research"
)

builder.add_edge(
    "research",
    "enrichment"
)

builder.add_edge(
    "enrichment",
    "scoring"
)

builder.add_edge(
    "scoring",
    "personalization"
)

builder.add_edge(
    "personalization",
    "email"
)

builder.add_edge(
    "email",
    "review"
)

builder.add_edge(
    "review",
    END
)

graph = builder.compile()
