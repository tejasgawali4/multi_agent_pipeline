"""
Agent 2 — Coding Agent
Converts the structured requirement into functional Python code.
Also handles re-generation when Code Review sends feedback.
"""

from langchain_core.messages import SystemMessage, HumanMessage
from graph.state import AgentState
from agents.llm_loader import get_llm

SYSTEM_PROMPT = """You are an expert Python software engineer.
Your job is to write clean, functional, well-structured Python code based on
the given software requirement specification.

Rules:
- Write complete, runnable Python code.
- Use proper module structure with functions and/or classes.
- Include inline comments explaining key logic.
- Handle edge cases and basic error handling (try/except where appropriate).
- Do NOT write tests or documentation — only the implementation code.
- Output ONLY the Python code block, no explanations outside the code.
- Start your response with ```python and end with ```
"""

REVISION_PROMPT = """You are an expert Python software engineer doing a code revision.
You previously wrote code that failed a code review. Below you will receive:
1. The original requirement
2. Your previously written code
3. The reviewer's feedback

Your job is to fix the issues mentioned in the feedback and produce improved code.

Rules:
- Address every point in the reviewer's feedback.
- Keep the code clean, functional, and well-commented.
- Output ONLY the Python code block.
- Start your response with ```python and end with ```
"""


def _extract_code(raw: str) -> str:
    """Strip markdown code fences from LLM output."""
    if "```python" in raw:
        raw = raw.split("```python", 1)[1]
    if "```" in raw:
        raw = raw.split("```", 1)[0]
    return raw.strip()


def coding_node(state: AgentState) -> AgentState:
    """
    LangGraph node for the Coding Agent.
    Reads: state["structured_requirement"], state["generated_code"], state["review_feedback"]
    Writes: state["generated_code"], state["review_iterations"]
    """
    iterations = state.get("review_iterations", 0)
    is_revision = iterations > 0 and state.get("review_feedback", "")

    if is_revision:
        print(f"\n[Agent 2] Coding Agent running (Revision #{iterations})...")
    else:
        print("\n[Agent 2] Coding Agent running (Initial generation)...")

    llm = get_llm()

    if is_revision:
        user_msg = (
            f"## Original Requirement\n{state['structured_requirement']}\n\n"
            f"## Previously Written Code\n```python\n{state['generated_code']}\n```\n\n"
            f"## Reviewer Feedback\n{state['review_feedback']}\n\n"
            "Please fix all issues and return the improved code."
        )
        messages = [
            SystemMessage(content=REVISION_PROMPT),
            HumanMessage(content=user_msg),
        ]
    else:
        user_msg = (
            f"Here is the structured software requirement:\n\n{state['structured_requirement']}"
        )
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_msg),
        ]

    response = llm.invoke(messages)
    code = _extract_code(response.content)

    print("[Agent 2] Done. Code generated.")
    return {
        **state,
        "generated_code": code,
        "review_iterations": iterations + 1,
    }
