from typing import Literal

from langgraph.graph import END, START, StateGraph

from agents.email_agent import generate_email
from agents.enrichment_agent import enrich_lead
from agents.knowledge_agent import get_company_knowledge
from agents.lead_scoring_agent import score_lead
from agents.personalization_agent import generate_personalization
from agents.research_agent import research_company
from agents.reviewer_agent import review_outreach
from graph.state import SDRState

MAX_REVISIONS = 2


def knowledge_node(state: SDRState) -> dict:
    return {"knowledge": get_company_knowledge(state["company"])}


def research_node(state: SDRState) -> dict:
    return {"research": research_company(state["company"])}


def enrichment_node(state: SDRState) -> dict:
    return {"enrichment": enrich_lead(state["company"])}


def scoring_node(state: SDRState) -> dict:
    if state["research"] is None:
        raise ValueError("Research is required before lead scoring")
    return {"lead_score": score_lead(state["research"])}


def personalization_node(state: SDRState) -> dict:
    if state["research"] is None or state["enrichment"] is None:
        raise ValueError("Research and enrichment are required for personalization")
    return {
        "personalization": generate_personalization(
            state["research"], state["knowledge"], state["enrichment"]
        )
    }


def email_node(state: SDRState) -> dict:
    if state["personalization"] is None:
        raise ValueError("Personalization is required before email generation")
    return {
        "email": generate_email(state["company"], state["personalization"])
    }


def review_node(state: SDRState) -> dict:
    if (
        state["research"] is None
        or state["personalization"] is None
        or state["email"] is None
    ):
        raise ValueError("Research, personalization, and email are required for review")
    return {
        "review": review_outreach(
            state["research"], state["personalization"], state["email"]
        )
    }


def revise_email_node(state: SDRState) -> dict:
    if state["personalization"] is None or state["review"] is None:
        raise ValueError("Personalization and review are required for revision")
    return {
        "email": generate_email(
            state["company"],
            state["personalization"],
            state["review"].revision_instructions,
        ),
        "revision_count": state["revision_count"] + 1,
    }


def route_after_review(state: SDRState) -> Literal["revise_email", "__end__"]:
    review = state["review"]
    if review is None or review.approved or state["revision_count"] >= MAX_REVISIONS:
        return END
    return "revise_email"


def build_workflow():
    builder = StateGraph(SDRState)
    builder.add_node("knowledge", knowledge_node)
    builder.add_node("research", research_node)
    builder.add_node("enrichment", enrichment_node)
    builder.add_node("scoring", scoring_node)
    builder.add_node("personalization", personalization_node)
    builder.add_node("email", email_node)
    builder.add_node("review", review_node)
    builder.add_node("revise_email", revise_email_node)

    builder.add_edge(START, "knowledge")
    builder.add_edge("knowledge", "research")
    builder.add_edge("research", "enrichment")
    builder.add_edge("enrichment", "scoring")
    builder.add_edge("scoring", "personalization")
    builder.add_edge("personalization", "email")
    builder.add_edge("email", "review")
    builder.add_conditional_edges("review", route_after_review)
    builder.add_edge("revise_email", "review")
    return builder.compile()


workflow = build_workflow()


def run_pipeline(company: str) -> dict:
    initial_state: SDRState = {
        "company": company,
        "knowledge": "",
        "research": None,
        "enrichment": None,
        "lead_score": None,
        "personalization": None,
        "email": None,
        "review": None,
        "revision_count": 0,
    }
    result = workflow.invoke(initial_state)
    serialized = {
        key: value.model_dump() if hasattr(value, "model_dump") else value
        for key, value in result.items()
    }
    if isinstance(serialized.get("review"), dict):
        serialized["review"]["revision_count"] = serialized["revision_count"]
    return serialized
