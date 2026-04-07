# 🤖 Multi-Agent Code Pipeline

A LangGraph-powered multi-agent system that takes a natural language software requirement and automatically produces:
- ✅ Structured requirements spec
- ✅ Working Python code (with review loop)
- ✅ Code review with iterative improvement
- ✅ Markdown documentation
- ✅ Pytest test cases
- ✅ Deployment configuration (Dockerfile, docker-compose, setup script)

All powered by HuggingFace open-source models via the Inference API — no OpenAI key needed.

---

## 🏗️ Architecture

```
[User Input]
     ↓
[1. Requirements Agent]   → structured_requirement
     ↓
[2. Coding Agent]         → generated_code
     ↓
[3. Code Review Agent]    → review_passed / review_feedback
     ↓ (if FAIL → back to Coding Agent, max 3 retries)
[4. Documentation Agent]  → documentation
     ↓
[5. Test Case Agent]      → test_cases
     ↓
[6. Deployment Agent]     → deploy_script
     ↓
[Streamlit UI]            → displays all outputs
```

The **Code Review loop** is implemented as a LangGraph conditional edge:
- If the review passes → move forward to Documentation
- If the review fails AND retries < 3 → send back to Coding Agent with feedback
- If retries ≥ 3 → force forward with best available code

---

## 📁 Project Structure

```
multi_agent_pipeline/
├── agents/
│   ├── llm_loader.py          # HuggingFace LLM setup (shared by all agents)
│   ├── requirements_agent.py  # Agent 1
│   ├── coding_agent.py        # Agent 2
│   ├── review_agent.py        # Agent 3
│   ├── docs_agent.py          # Agent 4
│   ├── test_agent.py          # Agent 5
│   └── deploy_agent.py        # Agent 6
├── graph/
│   ├── state.py               # AgentState TypedDict (shared state)
│   └── pipeline.py            # LangGraph graph wiring & conditional edge
├── app.py                     # Streamlit UI
├── requirements.txt
├── .env
└── README.md
```

---

## 🚀 Setup & Running

### 1. Clone / unzip the project

```bash
cd multi_agent_pipeline
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure your HuggingFace token

```bash
# Edit .env and replace hf_your_token_here with your actual token
```

Get a free token at: https://huggingface.co/settings/tokens  
*(Free account is sufficient — Inference API is included)*

### 5. Run the Streamlit UI

```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser.

---

## 🔧 Changing the Model

Edit `agents/llm_loader.py` and change `DEFAULT_MODEL`:

```python
# Fast and reliable (default)
DEFAULT_MODEL = "mistralai/Mistral-7B-Instruct-v0.3"

# Higher quality, slower
DEFAULT_MODEL = "mistralai/Mixtral-8x7B-Instruct-v0.1"

# Alternative
DEFAULT_MODEL = "HuggingFaceH4/zephyr-7b-beta"
```

---

## 🧪 Running the Pipeline Programmatically

```python
from graph.pipeline import build_pipeline
from graph.state import AgentState

pipeline = build_pipeline()

result = pipeline.invoke({
    "user_requirement": "Build a Flask REST API for a todo list with CRUD operations",
    "structured_requirement": "",
    "generated_code": "",
    "review_feedback": "",
    "review_passed": False,
    "review_iterations": 0,
    "documentation": "",
    "test_cases": "",
    "deploy_script": "",
})

print(result["generated_code"])
print(result["documentation"])
print(result["test_cases"])
```

---

## 📦 Tech Stack

| Component | Library |
|-----------|---------|
| Agent orchestration | `langgraph` |
| LLM integration | `langchain-huggingface` |
| LLM model | Mistral-7B-Instruct (HuggingFace Inference API) |
| UI | `streamlit` |
| State management | LangGraph `TypedDict` state |

---

## ⚠️ Notes

- HuggingFace free tier has rate limits. If you hit them, wait a minute and retry.
- The pipeline makes 6+ LLM calls per run. Each call may take 10–30 seconds on free tier.
- For faster results, consider upgrading to HuggingFace PRO for dedicated endpoints.
