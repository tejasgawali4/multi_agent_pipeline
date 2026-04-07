"""
Agent 1 — Requirements Agent
Takes raw natural language input and refines it into a structured
software requirement specification.
"""

from langchain_core.messages import SystemMessage, HumanMessage
from graph.state import AgentState
from agents.llm_loader import get_llm

SYSTEM_PROMPT = """You are a senior software requirements analyst.
Your job is to take a vague or informal software requirement written in natural language
and convert it into a clear, structured requirement specification.

Output format (strictly follow this):
---
## Project Title
<short title>

## Overview
<2-3 sentence summary of what needs to be built>

## Functional Requirements
- FR1: <requirement>
- FR2: <requirement>
- ...

## Non-Functional Requirements
- NFR1: <requirement>
- ...

## Inputs & Outputs
- Input: <what the system receives>
- Output: <what the system produces>

## Constraints & Assumptions
- <any technical or business constraints>
---

Be specific, concise, and unambiguous. Do not write code.
"""


def requirements_node(state: AgentState) -> AgentState:
    """
    LangGraph node for the Requirements Agent.
    Reads: state["user_requirement"]
    Writes: state["structured_requirement"]
    """
    print("\n[Agent 1] Requirements Agent running...")

    llm = get_llm()

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Here is the user's raw requirement:\n\n{state['user_requirement']}"),
    ]

    response = llm.invoke(messages)
    structured = response.content.strip()

    print("[Agent 1] Done. Structured requirement generated.")
    return {**state, "structured_requirement": structured}
