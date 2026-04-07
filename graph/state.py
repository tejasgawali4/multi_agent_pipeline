"""
Shared state schema for the Multi-Agent Pipeline.
Every agent reads from and writes to this single TypedDict.
"""

from typing import TypedDict


class AgentState(TypedDict):
    # --- Input ---
    user_requirement: str            # Raw natural language input from the user

    # --- Agent Outputs ---
    structured_requirement: str      # Requirements Agent output
    generated_code: str              # Coding Agent output
    review_feedback: str             # Code Review Agent feedback
    review_passed: bool              # Whether code passed review
    review_iterations: int           # Loop counter to cap retries at 3
    documentation: str               # Documentation Agent output
    test_cases: str                  # Test Case Agent output
    deploy_script: str               # Deployment Agent output
