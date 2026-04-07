"""
app.py — Streamlit UI for the Multi-Agent Pipeline.

Run with:
    streamlit run app.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from graph.pipeline import build_pipeline
from graph.state import AgentState

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Multi-Agent Code Pipeline",
    page_icon="🤖",
    layout="wide",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #1e1e2e;
        border-radius: 6px;
        padding: 6px 16px;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: #313244 !important;
    }
    .agent-badge {
        display: inline-block;
        background: #313244;
        color: #cdd6f4;
        border-radius: 20px;
        padding: 2px 12px;
        font-size: 0.78rem;
        margin-bottom: 8px;
        font-weight: 600;
        letter-spacing: 0.04em;
    }
    .status-pass { color: #a6e3a1; font-weight: bold; }
    .status-fail { color: #f38ba8; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("🤖 Multi-Agent Code Pipeline")
st.caption("Powered by LangGraph + HuggingFace Inference API")
st.divider()

# ── Sidebar — Settings ─────────────────────────────────────────────────────────
with st.sidebar:
    # st.header("⚙️ Settings")

    st.markdown("---")
    st.markdown("**Pipeline Agents**")
    st.markdown("""
1. 📋 Requirements Analyst  
2. 💻 Coding Agent  
3. 🔍 Code Reviewer *(with retry loop)*  
4. 📝 Documentation Agent  
5. 🧪 Test Case Agent  
6. 🚀 Deployment Agent  
    """)

    st.markdown("---")
    st.caption("Model: `meta-llama/Llama-3.1-8B-Instruct`")

# ── Main Input ─────────────────────────────────────────────────────────────────
col1, col2 = st.columns([3, 1])
with col1:
    user_requirement = st.text_area(
        "📝 Describe what you want to build",
        height=140,
        placeholder=(
            "Example: Build a REST API with Flask that allows users to create, "
            "read, update, and delete (CRUD) todo items stored in memory. "
            "Each todo item should have an id, title, description, and status field."
        ),
    )

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    run_button = st.button("🚀 Run Pipeline", use_container_width=True, type="primary")
    clear_button = st.button("🗑️ Clear Results", use_container_width=True)

if clear_button:
    for key in ["pipeline_result", "pipeline_error", "pipeline_log"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

# ── Run Pipeline ───────────────────────────────────────────────────────────────
if run_button:
    if not user_requirement.strip():
        st.warning("Please enter a requirement before running the pipeline.")
    elif not os.getenv("HF_TOKEN"):
        st.error("Please enter your HuggingFace API Token in the sidebar.")
    else:
        st.session_state.pop("pipeline_result", None)
        st.session_state.pop("pipeline_error", None)

        log_lines = []
        progress_bar = st.progress(0, text="Starting pipeline...")
        status_placeholder = st.empty()

        STEPS = [
            (1/6, "📋 Agent 1: Analysing requirements..."),
            (2/6, "💻 Agent 2: Generating code..."),
            (3/6, "🔍 Agent 3: Reviewing code..."),
            (4/6, "📝 Agent 4: Writing documentation..."),
            (5/6, "🧪 Agent 5: Generating test cases..."),
            (6/6, "🚀 Agent 6: Building deployment config..."),
        ]

        try:
            pipeline = build_pipeline()

            initial_state: AgentState = {
                "user_requirement": user_requirement,
                "structured_requirement": "",
                "generated_code": "",
                "review_feedback": "",
                "review_passed": False,
                "review_iterations": 0,
                "documentation": "",
                "test_cases": "",
                "deploy_script": "",
            }

            # Stream steps for live progress feedback
            step_idx = 0
            final_state = None

            for event in pipeline.stream(initial_state):
                node_name = list(event.keys())[0]
                node_state = event[node_name]

                node_labels = {
                    "requirements": (1/6, "📋 Requirements done. Running Coding Agent..."),
                    "coding":       (2/6, "💻 Code generated. Running Code Review..."),
                    "review":       (3/6, "🔍 Code review complete. Running Documentation..."),
                    "docs":         (4/6, "📝 Documentation done. Generating Tests..."),
                    "test":         (5/6, "🧪 Tests done. Building Deployment Config..."),
                    "deploy":       (6/6, "✅ All agents complete!"),
                }

                if node_name in node_labels:
                    progress, label = node_labels[node_name]
                    progress_bar.progress(progress, text=label)
                    log_lines.append(f"✓ {node_name.upper()} agent finished")

                final_state = node_state

            st.session_state["pipeline_result"] = final_state
            st.session_state["pipeline_log"] = log_lines
            progress_bar.empty()
            status_placeholder.success("✅ Pipeline completed successfully!")

        except Exception as e:
            progress_bar.empty()
            st.session_state["pipeline_error"] = str(e)

# ── Display Results ────────────────────────────────────────────────────────────
if "pipeline_error" in st.session_state:
    st.error(f"Pipeline error: {st.session_state['pipeline_error']}")

if "pipeline_result" in st.session_state:
    result: AgentState = st.session_state["pipeline_result"]

    st.divider()
    st.subheader("📊 Pipeline Results")

    # Quick stats row
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Review Iterations", result.get("review_iterations", 0))
    m2.metric("Review Status", "✅ Pass" if result.get("review_passed") else "⚠️ Forced")
    m3.metric("Code Lines", len(result.get("generated_code", "").splitlines()))
    m4.metric("Test Lines", len(result.get("test_cases", "").splitlines()))

    st.markdown("<br>", unsafe_allow_html=True)

    # Tabs for each agent output
    tabs = st.tabs([
        "📋 Requirements",
        "💻 Code",
        "🔍 Review",
        "📝 Docs",
        "🧪 Tests",
        "🚀 Deployment",
    ])

    with tabs[0]:
        st.markdown('<span class="agent-badge">Agent 1 — Requirements Analyst</span>', unsafe_allow_html=True)
        st.markdown(result.get("structured_requirement", "_No output_"))

    with tabs[1]:
        st.markdown('<span class="agent-badge">Agent 2 — Coding Agent</span>', unsafe_allow_html=True)
        st.code(result.get("generated_code", "# No code generated"), language="python")
        st.download_button(
            "⬇️ Download main.py",
            data=result.get("generated_code", ""),
            file_name="main.py",
            mime="text/plain",
        )

    with tabs[2]:
        st.markdown('<span class="agent-badge">Agent 3 — Code Reviewer</span>', unsafe_allow_html=True)
        feedback = result.get("review_feedback", "_No review_")
        passed = result.get("review_passed", False)
        if passed:
            st.markdown('<p class="status-pass">✅ REVIEW PASSED</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="status-fail">⚠️ FORCED FORWARD (max iterations reached)</p>', unsafe_allow_html=True)
        st.markdown(feedback)

    with tabs[3]:
        st.markdown('<span class="agent-badge">Agent 4 — Documentation Agent</span>', unsafe_allow_html=True)
        st.markdown(result.get("documentation", "_No documentation_"))
        st.download_button(
            "⬇️ Download DOCUMENTATION.md",
            data=result.get("documentation", ""),
            file_name="DOCUMENTATION.md",
            mime="text/plain",
        )

    with tabs[4]:
        st.markdown('<span class="agent-badge">Agent 5 — Test Case Agent</span>', unsafe_allow_html=True)
        st.code(result.get("test_cases", "# No tests generated"), language="python")
        st.download_button(
            "⬇️ Download test_main.py",
            data=result.get("test_cases", ""),
            file_name="test_main.py",
            mime="text/plain",
        )

    with tabs[5]:
        st.markdown('<span class="agent-badge">Agent 6 — Deployment Agent</span>', unsafe_allow_html=True)
        st.markdown(result.get("deploy_script", "_No deployment config_"))
        st.download_button(
            "⬇️ Download deploy_config.md",
            data=result.get("deploy_script", ""),
            file_name="deploy_config.md",
            mime="text/plain",
        )
