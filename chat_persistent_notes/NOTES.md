# Chat Persistent Notes

Use this file to store anything you want me to remember between sessions and projects.

## How to use
- At the start of every new session, say: **"Read chat_persistent_notes/NOTES.md first."**
- Update this file as features are completed or priorities change.

---

## Project: BzHub

**What it is:** Full-stack web ERP/business management app. SMB-focused, Odoo-inspired. Goal is multi-tenant SaaS.

**Stack:**
- Frontend: Next.js 14 (App Router), Tailwind CSS, shadcn/ui
- Database: Supabase (PostgreSQL), RLS enabled
- Deployment: Vercel (auto-deploy on push to `main`)
- Repo: `/Users/scottvalentino/BzHub`
- Web app: `bzhub_web/bzhub_web/`

**Current version:** v4.7.0 (2026-03-12) — live on Vercel

**Live modules:** Dashboard, Operations (Inventory, POS, Bills, Suppliers, Purchase Orders), HR (Employees, Payroll, Goals, Appraisals, Skills, Leave), CRM (Contacts, Leads, Kanban), Reports, Settings (incl. Industry Templates), Help, Employee Self-Service Portal

**Known gap:** Login is hardcoded `admin/admin123` — no real auth yet (FEAT-036, planned Phase 3).

**Next feature to build:** FEAT-039 — Offline-First Mode

---

## Ultimate Goal (Keep This in Mind Always)
> **WhatsApp-first operations + Multi-tenant SaaS.** All features should be built with this end-state in mind — notifications extensible to WhatsApp, data models org-aware from the start.

---

## Pending Features (Priority Order)

### 🔴 Phase 1 — Core Product Features
1. ~~**FEAT-034** — Approval Workflows~~ ✅ Done (v4.4.0)
2. ~~**FEAT-035** — Employee Self-Service Portal~~ ✅ Done (v4.5.0)
3. ~~**FEAT-021**~~ ✅ Done v4.6.0 — In-app Notification Center
4. ~~**FEAT-023**~~ ✅ Done v4.6.0 — Customizable Dashboard
5. ~~**FEAT-024**~~ ✅ Done v4.6.0 — CSV Export
6. ~~**FEAT-025**~~ ✅ Done v4.6.0 — Global Search
7. ~~**FEAT-026**~~ ✅ Done v4.6.0 — Audit Log

### 🟠 Phase 2 — USP / Differentiation
8. ~~**FEAT-038**~~ ✅ Done (v4.7.0) — Industry-Specific Templates (Retail, Clinic, Restaurant, Distributor — one-click setup)
9. **FEAT-039** — Offline-First Mode ← **START HERE NEXT SESSION** (works without internet, syncs on reconnect)
10. **FEAT-040** — GST / Tax Compliance India (GST invoicing, GSTR-1/3B export — compete with Tally)
11. **FEAT-032** — AI-Powered Insights (stock forecasting, HR nudges, sales anomaly, NL queries)

### 🔵 Phase 3 — Multi-User & SaaS Architecture
12. **FEAT-036** — Supabase Auth (real login — blocker for multi-tenancy)
13. **FEAT-022** — RBAC (Admin, Manager, Employee role gates)
14. **FEAT-037** — Multi-Tenancy (org isolation via RLS + `organization_id` on all tables)

### 🟣 Phase 4 — The Crown Jewel
15. **FEAT-033** — WhatsApp / SMS (run operations via WhatsApp, invoice pay links, alerts)

### ⚙️ Architecture (ongoing)
- **FEAT-031** — Workspace Reorganization
- **FEAT-SUPABASE** — Complete Supabase migration
- **FEAT-XXX** — Refactor: decouple UI from business logic

---

## Completed (Recent)
- v4.7.0 — Industry-Specific Templates (Retail, Clinic, Restaurant, Distributor, General)
- v4.6.0 — Notification Center, Dashboard Customization, CSV Export, Global Search, Audit Log
- v4.5.0 — Employee Self-Service Portal (My Goals, My Appraisals, My Leave, My Skills)
- v4.4.0 — Approval Workflows (Leave Requests, Purchase Orders, Appraisal Sign-off)
- v4.3.0 — Goals, Appraisals, Skills Matrix
- v4.2.0 — Reports page, Supplier management
- v4.1.x — Vercel deploy, Supabase integration, mobile responsive, Supabase schema v2

---

## Rules (Always Follow — Every Feature)
After every feature is completed, update ALL of these without being asked:
1. `documentation/FEATURE_REQUESTS_AND_BUGS.md` — mark Done, update status
2. `documentation/RELEASE_NOTES_v4.1.md` — add new version entry
3. `chat_persistent_notes/NOTES.md` — tick off feature, update version, set next feature
4. Memory files at `.claude/projects/.../memory/` — update project state
5. `bzhub_web/bzhub_web/src/app/help/page.tsx` — add help section for new feature

---

## Session Opener Template
1. "Read chat_persistent_notes/NOTES.md first."
2. State goal for this session (e.g. "Let's do FEAT-036 Supabase Auth")
3. Any constraints (design, tech, deadlines)
4. Any errors or blockers
