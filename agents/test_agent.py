"""
Agent 5 — Test Case Agent
Generates unit tests and integration tests for the approved code.
"""

from langchain_core.messages import SystemMessage, HumanMessage
from graph.state import AgentState
from agents.llm_loader import get_llm

SYSTEM_PROMPT = """You are a senior Python QA engineer specialising in test-driven development.
Your job is to write comprehensive pytest test cases for the given Python code.

Requirements for your tests:
- Use pytest as the testing framework.
- Write at least one unit test per function/method.
- Include at least one integration test that tests the overall flow.
- Test both happy paths (expected inputs) and edge cases (empty input, wrong types, boundary values).
- Use pytest.mark.parametrize where applicable to test multiple inputs efficiently.
- Add a brief docstring to each test function explaining what it tests.
- Mock external dependencies (file I/O, API calls, DB calls) using unittest.mock or pytest-mock.
- Output ONLY the Python test code block.
- Start your response with ```python and end with ```
"""


def _extract_code(raw: str) -> str:
    """Strip markdown code fences from LLM output."""
    if "```python" in raw:
        raw = raw.split("```python", 1)[1]
    if "```" in raw:
        raw = raw.split("```", 1)[0]
    return raw.strip()


def test_node(state: AgentState) -> AgentState:
    """
    LangGraph node for the Test Case Agent.
    Reads: state["generated_code"], state["structured_requirement"]
    Writes: state["test_cases"]
    """
    print("\n[Agent 5] Test Case Agent running...")

    llm = get_llm()

    user_msg = (
        f"## Software Requirement\n{state['structured_requirement']}\n\n"
        f"## Python Code to Test\n```python\n{state['generated_code']}\n```\n\n"
        "Write comprehensive pytest tests covering unit tests, edge cases, and at least one integration test."
    )

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_msg),
    ]

    response = llm.invoke(messages)
    tests = _extract_code(response.content)

    print("[Agent 5] Done. Test cases generated.")
    return {**state, "test_cases": tests}
