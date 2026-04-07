"""
Agent 3 — Code Review Agent
Reviews generated code for correctness, efficiency, and security.
Sets review_passed = True/False to control the LangGraph conditional edge.
"""

from langchain_core.messages import SystemMessage, HumanMessage
from graph.state import AgentState
from agents.llm_loader import get_llm

SYSTEM_PROMPT = """You are a senior Python code reviewer with expertise in software quality,
security, and best practices.

Your job is to review the provided Python code against the given requirements.

Evaluate the code on:
1. Correctness — Does it fulfill all functional requirements?
2. Code Quality — Is it readable, well-structured, and Pythonic?
3. Error Handling — Are edge cases and exceptions handled properly?
4. Security — Are there any obvious security issues (e.g. SQL injection, unvalidated input)?
5. Efficiency — Are there any obvious performance problems?

Your response MUST follow this exact format:
---
## Review Result: PASS  (or FAIL)

## Summary
<1-2 sentence overall assessment>

## Issues Found
- Issue 1: <description> (Severity: High/Medium/Low)
- Issue 2: ...
(write "None" if no issues)

## Recommendations
- <specific actionable fix>
(write "None" if no recommendations)
---

IMPORTANT: Write "PASS" only if the code is correct, handles errors reasonably,
and fulfills the requirements. Write "FAIL" if there are any High or Medium severity issues.
"""


def _parse_verdict(review_text: str) -> bool:
    """
    Extract PASS/FAIL from the review text.
    Returns True if PASS, False if FAIL.
    """
    upper = review_text.upper()
    # Look for explicit verdict line
    for line in upper.splitlines():
        if "REVIEW RESULT:" in line:
            return "PASS" in line
    # Fallback: count occurrences
    return upper.count("PASS") > upper.count("FAIL")


def review_node(state: AgentState) -> AgentState:
    """
    LangGraph node for the Code Review Agent.
    Reads: state["generated_code"], state["structured_requirement"]
    Writes: state["review_feedback"], state["review_passed"]
    """
    print("\n[Agent 3] Code Review Agent running...")

    llm = get_llm()

    user_msg = (
        f"## Software Requirement\n{state['structured_requirement']}\n\n"
        f"## Code to Review\n```python\n{state['generated_code']}\n```"
    )

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_msg),
    ]

    response = llm.invoke(messages)
    feedback = response.content.strip()
    passed = _parse_verdict(feedback)

    status = "✅ PASSED" if passed else "❌ FAILED"
    print(f"[Agent 3] Done. Review result: {status}")

    return {
        **state,
        "review_feedback": feedback,
        "review_passed": passed,
    }
