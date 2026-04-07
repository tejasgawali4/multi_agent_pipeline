"""
LangGraph Pipeline — wires all 6 agents into a sequential graph
with a conditional review loop (max 3 retries).

Graph flow:
  START
    → requirements_node
    → coding_node
    → review_node  ──(FAIL, iterations < 3)──→ coding_node
         ↓ (PASS or iterations >= 3)
    → docs_node
    → test_node
    → deploy_node
    → END
"""

from langgraph.graph import StateGraph, END

from graph.state import AgentState
from agents.requirements_agent import requirements_node
from agents.coding_agent import coding_node
from agents.review_agent import review_node
from agents.docs_agent import docs_node
from agents.test_agent import test_node
from agents.deploy_agent import deploy_node

MAX_REVIEW_ITERATIONS = 3


def review_router(state: AgentState) -> str:
    """
    Conditional edge function called after review_node.
    Returns:
        "coding"   → loop back for a code revision
        "docs"     → move forward to documentation
    """
    passed = state.get("review_passed", False)
    iterations = state.get("review_iterations", 0)

    if passed:
        print(f"\n[Router] Code PASSED review after {iterations} iteration(s). Moving forward.")
        return "docs"

    if iterations >= MAX_REVIEW_ITERATIONS:
        print(f"\n[Router] Max iterations ({MAX_REVIEW_ITERATIONS}) reached. Forcing forward with best code.")
        return "docs"

    print(f"\n[Router] Code FAILED review (iteration {iterations}). Sending back to Coding Agent.")
    return "coding"


def build_pipeline() -> StateGraph:
    """
    Builds and compiles the LangGraph StateGraph.

    Returns:
        Compiled LangGraph app ready for .invoke() calls.
    """
    graph = StateGraph(AgentState)

    # --- Register nodes ---
    graph.add_node("requirements", requirements_node)
    graph.add_node("coding", coding_node)
    graph.add_node("review", review_node)
    graph.add_node("docs", docs_node)
    graph.add_node("test", test_node)
    graph.add_node("deploy", deploy_node)

    # --- Entry point ---
    graph.set_entry_point("requirements")

    # --- Linear edges ---
    graph.add_edge("requirements", "coding")
    graph.add_edge("coding", "review")

    # --- Conditional edge: review loop ---
    graph.add_conditional_edges(
        "review",
        review_router,
        {
            "coding": "coding",   # loop back
            "docs": "docs",       # move forward
        }
    )

    # --- Remaining sequential edges ---
    graph.add_edge("docs", "test")
    graph.add_edge("test", "deploy")
    graph.add_edge("deploy", END)

    return graph.compile()
