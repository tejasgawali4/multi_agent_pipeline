"""
Agent 4 — Documentation Agent
Generates structured Markdown documentation for the approved code.
"""

from langchain_core.messages import SystemMessage, HumanMessage
from graph.state import AgentState
from agents.llm_loader import get_llm

SYSTEM_PROMPT = """You are a technical writer and Python expert.
Your job is to generate clear, structured Markdown documentation for the given Python code.

The documentation must include:

# <Project Title>

## Overview
<What the code does, in plain English>

## Architecture
<Brief description of the module/class/function structure>

## Functions / Classes Reference
For each function or class, document:
- **Name**: function or class name
- **Purpose**: what it does
- **Parameters**: list with types and descriptions
- **Returns**: return type and description
- **Example usage**: a short code snippet

## Setup & Usage
<Step-by-step instructions to install dependencies and run the code>

## Error Handling
<How the code handles errors and edge cases>

Be thorough but concise. Use proper Markdown formatting.
"""


def docs_node(state: AgentState) -> AgentState:
    """
    LangGraph node for the Documentation Agent.
    Reads: state["generated_code"], state["structured_requirement"]
    Writes: state["documentation"]
    """
    print("\n[Agent 4] Documentation Agent running...")

    llm = get_llm()

    user_msg = (
        f"## Software Requirement\n{state['structured_requirement']}\n\n"
        f"## Python Code to Document\n```python\n{state['generated_code']}\n```"
    )

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_msg),
    ]

    response = llm.invoke(messages)
    docs = response.content.strip()

    print("[Agent 4] Done. Documentation generated.")
    return {**state, "documentation": docs}
