"""
Agent 6 — Deployment Configuration Agent
Generates deployment scripts and configuration for the approved code.
"""

from langchain_core.messages import SystemMessage, HumanMessage
from graph.state import AgentState
from agents.llm_loader import get_llm

SYSTEM_PROMPT = """You are a senior DevOps engineer and Python deployment specialist.
Your job is to generate a complete deployment configuration for a Python project.

You must generate ALL of the following, clearly separated with headers:

---

## 1. requirements.txt
List all pip packages needed. Infer them from the imports in the code.
Always include a version pin (e.g. flask==3.0.0).

## 2. Dockerfile
A production-ready Dockerfile using python:3.11-slim as base.
Include: WORKDIR, COPY, RUN pip install, EXPOSE (if web app), CMD.

## 3. docker-compose.yml
A basic docker-compose.yml to build and run the container.
Include environment variable support via .env file.

## 4. setup.sh
A bash script that:
- Creates and activates a Python virtual environment
- Installs dependencies
- Runs the application

## 5. .env.example
Template for required environment variables with placeholder values.

---

Be specific to the actual code provided. Do not generate generic boilerplate.
"""


def deploy_node(state: AgentState) -> AgentState:
    """
    LangGraph node for the Deployment Agent.
    Reads: state["generated_code"], state["structured_requirement"]
    Writes: state["deploy_script"]
    """
    print("\n[Agent 6] Deployment Agent running...")

    llm = get_llm()

    user_msg = (
        f"## Software Requirement\n{state['structured_requirement']}\n\n"
        f"## Python Code to Deploy\n```python\n{state['generated_code']}\n```\n\n"
        "Generate the full deployment configuration as described."
    )

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_msg),
    ]

    response = llm.invoke(messages)
    deploy = response.content.strip()

    print("[Agent 6] Done. Deployment configuration generated.")
    return {**state, "deploy_script": deploy}
