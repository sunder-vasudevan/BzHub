# Workspace Context Optimization Summary

## 1. Frequently Referenced Files
- api/app.py, api/hr.py, api/inventory.py, api/pos.py, api/supabase_client.py, api/visitor.py
- src/core/lead_opportunity.py, src/config.py, src/services/*
- documentation/ARCHITECTURE.md, copilot-instructions.md, README.md
- scripts/bizhub.py, scripts/seed_dummy_data.py

## 2. Short Summaries for Major Files
- api/app.py: Main FastAPI app entry point, routes and API logic.
- api/hr.py: HR-related API endpoints and business logic.
- api/inventory.py: Inventory management endpoints and logic.
- api/pos.py: Point-of-sale endpoints and logic.
- api/supabase_client.py: Handles Supabase DB connections.
- src/core/lead_opportunity.py: Lead and opportunity management logic.
- src/services/: Service layer for analytics, HR, email, etc.
- documentation/ARCHITECTURE.md: High-level system architecture and design.
- copilot-instructions.md: Project setup and workflow checklist.
- README.md: Project overview and usage instructions.
- scripts/bizhub.py: Script to launch or manage BizHub.
- scripts/seed_dummy_data.py: Seeds the database with test data.

## 3. Context Map
- Key Modules: api (API endpoints), src/core (business logic), src/services (service layer), scripts (utilities), documentation (project docs)
- Dependencies: FastAPI, Supabase, custom service modules, Next.js (bzhub_web), Python standard libs
- Responsibilities: API (external interface), core (domain logic), services (supporting logic), scripts (automation), docs (reference)

## 4. Parts Not Needed in Context
- __pycache__ folders, build outputs, logs, assets (unless working on UI), test files (unless debugging tests), ideaboard/ and bzhub_web/ (unless working on frontend)

## 5. Compact Memory (≤15 lines)
- Reduced token usage and context for efficiency.
- Identified and summarized key files and modules.
- Provided a checklist for project setup and workflow.
- Advised closing large docs and unused files.
- Focused on essential instructions and active tasks.
- No major code changes made yet.
- Awaiting next user action or checklist item.
- Workspace includes Python backend, Next.js frontend, scripts, and docs.
- Main focus: API, core logic, services, and project documentation.
- Context map and summaries now available for quick reference.
- Irrelevant files and folders excluded from active context.
- Ready for next step or specific task.
- All steps for context optimization completed.
- Efficient, minimal context established.
- Let me know your next priority!
