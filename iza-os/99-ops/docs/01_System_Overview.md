# Chapter 1: IZA OS System Overview

## Project Status (As of September 9, 2025)

This document provides a snapshot of the IZA OS project, its current state, and a roadmap for future development. 

### Recent Accomplishments

1.  **System Deadlock Resolved:** The primary issue causing circular logic and lack of progress has been fixed. The root cause was a split-state problem between multiple conflicting orchestrators (some using JSON files, others using Redis). 
2.  **Orchestration Unified:** A single, definitive entry point has been created: `UNIFIED_ORCHESTRATOR.py`. This script now manages the entire system lifecycle.
3.  **State Management Centralized:** The system now uses a robust, Redis-based architecture for all agent and task management, managed by the `agent_coordinator.py` script. The old, brittle JSON state files (`AGENT_STATUS.json`, etc.) have been safely archived.
4.  **New Capabilities Integrated:** The system is now aware of three powerful new tools for rapid business prototyping. The core agent coordinator has been updated with new agent definitions to leverage these tools.
5.  **Idea Database Created:** A new file, `BUSINESS_IDEAS.json`, has been created to store and track your business ideas over time.

**Conclusion:** The system is now in a stable, healthy, and operational state, ready for the next phase of development.

---

## Getting Started

To run the Iza OS system, ensure your Redis server is running, then execute the following command from the root directory:

```bash
python3 UNIFIED_ORCHESTRATOR.py
```

This will initialize the agent coordinator and begin monitoring the system for tasks.

---

## Core Capabilities & Tools

We have identified and defined agents for a powerful new stack for rapid application development:

*   **Claudable (`Venture_Scaffolder` agent):** Builds a functional web application from a natural language description. Ideal for going from a new idea to a working codebase.
*   **open-lovable (`UI_Cloner` agent):** Clones an existing website's user interface into an editable React application. Perfect for rapidly prototyping based on an existing design.
*   **TweakCN (`UI_Stylist` agent):** A visual theme editor for `shadcn/ui` components. Allows for rapid customization of a UI's look and feel.

---

## Roadmap & Next Steps

This is a clear outline of what is left to be completed to make the system fully autonomous.

### Priority 1: Implement Agent Execution Logic

**Task:** The new agents (`Venture_Scaffolder`, `UI_Cloner`, `UI_Stylist`) are currently defined in `agent_coordinator.py` but have mock execution logic. The next critical step is to implement the real logic.

**Steps:**
1.  Modify the `_handle_custom` function in `/Users/divinejohns/memU/iza-os-core/kernel/core/agent_coordinator.py`.
2.  For the `Venture_Scaffolder` agent, add Python `subprocess` logic to execute the `npx claudable@latest` command.
3.  For the `UI_Cloner` agent, add logic to run the `open-lovable` tool from its directory, passing the required API keys and target URL.
4.  This will involve complex management of subprocess `stdin`, `stdout`, and environment variables to make the agents truly autonomous.

### Priority 2: Integrate the Idea Database

**Task:** Connect the `BUSINESS_IDEAS.json` file to the agent workflow.

**Steps:**
1.  Modify the `Problem_Discoverer` agent to write new ideas it finds into `BUSINESS_IDEAS.json`.
2.  Modify the `Venture_Scaffolder` agent to be able to read from `BUSINESS_IDEAS.json` and execute scaffolding on a pending idea.

### Priority 3: Fix Coordinator Bug

**Task:** The `agent_coordinator.py` script currently produces `RuntimeWarning: coroutine was never awaited` warnings during initialization. This is a non-fatal bug that should be fixed to improve code quality.

**Steps:**
1.  Investigate the `_initialize_agent` method in `agent_coordinator.py`.
2.  Ensure that any asynchronous functions called within it are correctly `await`ed, likely by making the `_initialize_agent` method itself `async`.

### Priority 4: Build an Interactive UI

**Task:** Create a simple user interface for managing Iza OS instead of using the command line.

**Steps:**
1.  Choose a simple framework like Streamlit or Gradio.
2.  Build a UI that calls the functions of the `UNIFIED_ORCHESTRATOR` and `AgentCoordinator`.
3.  The UI should allow you to: 
    *   View agent and task status.
    *   Submit new tasks (e.g., "Scaffold a new app from this idea...").
    *   View and manage the `BUSINESS_IDEAS.json` database.
