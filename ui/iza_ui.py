#!/usr/bin/env python3
"""
IZA OS Interactive UI

Streamlit application to manage IZA OS components:
- View agent and task status
- Submit new tasks
- View and manage BUSINESS_IDEAS.json
"""

import asyncio
import json
import sys
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import streamlit as st


# Paths
WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
BUSINESS_DATA_DIR = WORKSPACE_ROOT / "business_data"
BUSINESS_IDEAS_PATH = BUSINESS_DATA_DIR / "BUSINESS_IDEAS.json"


def ensure_business_ideas_file_exists() -> None:
    BUSINESS_DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not BUSINESS_IDEAS_PATH.exists():
        BUSINESS_IDEAS_PATH.write_text("[]\n", encoding="utf-8")


def load_business_ideas() -> List[Dict[str, Any]]:
    ensure_business_ideas_file_exists()
    try:
        return json.loads(BUSINESS_IDEAS_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []


def save_business_ideas(ideas: List[Dict[str, Any]]) -> None:
    BUSINESS_IDEAS_PATH.write_text(json.dumps(ideas, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def run_async(coro):
    return asyncio.run(coro)


@st.cache_resource(show_spinner=False)
def get_universal_api_orchestrator():
    # Lazy import to avoid global import-time side effects
    from core.api_orchestrator.UNIVERSAL_API_ORCHESTRATOR import UniversalAPIOrchestrator

    return UniversalAPIOrchestrator()


@st.cache_resource(show_spinner=False)
def get_memory_orchestrator():
    from core.memory_engine.UNIFIED_MEMORY_ORCHESTRATOR import UnifiedMemoryOrchestrator

    return UnifiedMemoryOrchestrator()


def load_agent_orchestrator_class():
    """Load the production Agent Orchestrator without polluting sys.modules.

    We avoid conflicting with the top-level `core` package by loading directly from file.
    """
    from importlib.machinery import SourceFileLoader

    orchestrator_file = WORKSPACE_ROOT / "iza-os-production" / "src" / "core" / "agent_orchestrator.py"
    if not orchestrator_file.exists():
        return None
    module = SourceFileLoader("iza_agent_orchestrator_module", str(orchestrator_file)).load_module()
    return getattr(module, "IZAOSAgentOrchestrator", None)


@st.cache_resource(show_spinner=False)
def get_agent_orchestrator():
    OrchestratorClass = load_agent_orchestrator_class()
    if OrchestratorClass is None:
        return None
    return OrchestratorClass()


def format_status_chip(status: str) -> str:
    status_lower = (status or "").lower()
    color = "gray"
    if status_lower in {"healthy", "connected", "completed", "success"}:
        color = "green"
    elif status_lower in {"running", "created", "synced", "active"}:
        color = "blue"
    elif status_lower in {"unhealthy", "failed", "error", "disconnected"}:
        color = "red"
    return f"<span style='background:{color};color:white;padding:2px 6px;border-radius:8px;font-size:0.8rem'>{status}</span>"


def page_status_dashboard():
    st.subheader("System Status")

    api_orch = get_universal_api_orchestrator()
    mem_orch = get_memory_orchestrator()
    agent_orch = get_agent_orchestrator()

    cols = st.columns(3)
    with cols[0]:
        st.markdown("**API Providers**")
        try:
            health = run_async(api_orch.health_check())
            for name, info in health.items():
                st.markdown(f"- {name}: {format_status_chip(info.get('status', 'unknown'))}", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"API health check failed: {e}")

    with cols[1]:
        st.markdown("**Memory Systems**")
        try:
            # Initialize and sync only on demand
            if st.button("Initialize Memory Systems", key="init_mem"):
                run_async(mem_orch.initialize_all_systems())
                run_async(mem_orch.sync_all_systems())
                st.success("Memory systems initialized and synced.")

            status = run_async(mem_orch.get_system_status())
            st.write({
                "total_memories": status.get("total_memories"),
                "systems": status.get("systems", {}),
            })
        except Exception as e:
            st.error(f"Memory status failed: {e}")

    with cols[2]:
        st.markdown("**Agent Orchestrator**")
        if agent_orch is None:
            st.warning("Agent Orchestrator not available.")
        else:
            try:
                tasks = getattr(agent_orch, "tasks", {})
                st.write({
                    "repositories": len(getattr(agent_orch, "repositories", {})),
                    "tasks": len(tasks),
                })
            except Exception as e:
                st.error(f"Agent orchestrator status failed: {e}")

    st.divider()
    st.subheader("Recent Tasks")
    if agent_orch is None:
        st.info("No tasks available.")
    else:
        try:
            tasks = getattr(agent_orch, "tasks", {})
            if not tasks:
                st.info("No tasks created yet.")
            else:
                rows = []
                for task_id, task in tasks.items():
                    record = asdict(task) if hasattr(task, "__dict__") else dict(task)
                    rows.append({
                        "id": record.get("id", task_id),
                        "type": record.get("type"),
                        "repository": record.get("repository"),
                        "status": record.get("status"),
                        "priority": record.get("priority"),
                        "created_at": record.get("created_at"),
                        "completed_at": record.get("completed_at"),
                    })
                st.dataframe(rows, use_container_width=True)
        except Exception as e:
            st.error(f"Failed to load tasks: {e}")


def page_submit_task():
    st.subheader("Submit New Task")
    agent_orch = get_agent_orchestrator()
    api_orch = get_universal_api_orchestrator()

    if agent_orch is None:
        st.warning("Agent Orchestrator unavailable. Task submission disabled.")
        return

    repos = sorted(list(getattr(agent_orch, "repositories", {}).keys()))
    if not repos:
        st.info("No repositories loaded in orchestrator.")

    with st.form("create_task_form"):
        repo = st.selectbox("Repository", options=repos, index=0 if repos else None)
        task_type = st.selectbox("Task Type", options=["analyze", "clone", "integrate"], index=0)
        execute_now = st.checkbox("Execute immediately")
        submitted = st.form_submit_button("Create Task")

        if submitted and repo:
            try:
                task_id = run_async(agent_orch.create_integration_task(repo, task_type))
                st.success(f"Task created: {task_id}")
                if execute_now:
                    with st.spinner("Executing task..."):
                        result = run_async(agent_orch.execute_task(task_id))
                        st.write(result)
            except Exception as e:
                st.error(f"Failed to create/execute task: {e}")

    st.divider()
    st.markdown("**Natural Language Task (optional)**")
    nl_task = st.text_area("Describe the task", placeholder="Scaffold a new app from this idea...", height=120)
    if st.button("Plan with AI"):
        try:
            prompt = (
                "Translate the following instruction into an actionable plan using these actions: "
                "analyze|clone|integrate on one of the known repositories. "
                "Respond as JSON with keys: repo (string from known repos), tasks (array of types).\n\n"
                f"Instruction: {nl_task}"
            )
            ai_reply = run_async(api_orch.smart_chat(prompt, max_tokens=300))
            st.code(ai_reply)
        except Exception as e:
            st.error(f"Planning failed: {e}")


def page_business_ideas():
    st.subheader("Business Ideas Database")

    ideas = load_business_ideas()

    with st.expander("Add New Idea", expanded=True):
        with st.form("add_idea_form"):
            title = st.text_input("Title", max_chars=200)
            description = st.text_area("Description", height=120)
            priority = st.selectbox("Priority", options=["LOW", "MEDIUM", "HIGH"], index=1)
            status = st.selectbox("Status", options=["pending", "approved", "in_progress", "launched", "archived"], index=0)
            submitted = st.form_submit_button("Add Idea")
            if submitted and title.strip():
                idea = {
                    "id": f"idea_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                    "title": title.strip(),
                    "description": description.strip(),
                    "priority": priority,
                    "status": status,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                }
                ideas.append(idea)
                save_business_ideas(ideas)
                st.success("Idea added.")
                st.experimental_rerun()

    st.markdown("**Ideas**")
    if not ideas:
        st.info("No ideas yet. Add one above.")
        return

    edited_rows = st.data_editor(
        ideas,
        key="ideas_editor",
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "id": st.column_config.Column(disabled=True),
            "created_at": st.column_config.Column(disabled=True),
        },
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Save Changes"):
            # Ensure timestamps are updated
            for row in edited_rows:
                row["updated_at"] = datetime.utcnow().isoformat()
            save_business_ideas(edited_rows)
            st.success("Ideas saved.")
    with col2:
        to_delete = st.text_input("Delete by ID", placeholder="idea_YYYYMMDD_HHMMSS")
        if st.button("Delete") and to_delete:
            new_list = [i for i in ideas if i.get("id") != to_delete]
            if len(new_list) != len(ideas):
                save_business_ideas(new_list)
                st.success(f"Deleted {to_delete}")
                st.experimental_rerun()
            else:
                st.warning("ID not found.")
    with col3:
        if st.download_button("Export JSON", data=json.dumps(ideas, indent=2), file_name="BUSINESS_IDEAS.json", mime="application/json"):
            pass


def main():
    st.set_page_config(page_title="IZA OS UI", page_icon="🤖", layout="wide")
    st.title("IZA OS UI")
    st.caption("Manage agents, tasks, and business ideas.")

    with st.sidebar:
        page = st.radio(
            "Navigate",
            options=["Status", "Submit Task", "Business Ideas"],
            index=0,
        )

    if page == "Status":
        page_status_dashboard()
    elif page == "Submit Task":
        page_submit_task()
    elif page == "Business Ideas":
        page_business_ideas()


if __name__ == "__main__":
    main()

