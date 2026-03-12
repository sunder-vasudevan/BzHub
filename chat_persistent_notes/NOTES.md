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

**Current version:** v4.3.0 (2026-03-11)

**Live modules:** Dashboard, Operations (Inventory, POS, Suppliers), HR (Employees, Payroll, Goals, Appraisals, Skills), CRM (Contacts, Leads, Kanban), Reports, Settings

**Known gap:** Login is hardcoded `admin/admin123` — no real auth yet.

---

## Ultimate Goal (Keep This in Mind Always)
> **WhatsApp-first operations + Multi-tenant SaaS.** All features should be built with this end-state in mind — notifications extensible to WhatsApp, data models org-aware from the start.

---

## Pending Features (Priority Order)

### 🔴 Phase 1 — Core Product Features
1. ~~**FEAT-034** — Approval Workflows~~ ✅ Done (v4.4.0)
2. **FEAT-035** — Employee Self-Service Portal (view goals, submit appraisal, apply leave)
3. **FEAT-021** — In-app Notification Center
4. **FEAT-023** — Customizable Dashboard (drag/drop KPI cards, chart types, date ranges)
5. **FEAT-024** — Export/Import (Excel, PDF, CSV)
6. **FEAT-025** — Advanced Search & Filters (global search, group by, saved filters)
7. **FEAT-026** — Audit Log (who changed what and when)

### 🟠 Phase 2 — USP / Differentiation
8. **FEAT-038** — Industry-Specific Templates (Retail, Clinic, Restaurant, Distributor — one-click setup)
9. **FEAT-039** — Offline-First Mode (works without internet, syncs on reconnect)
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
- v4.4.0 — Approval Workflows (Leave Requests, Purchase Orders, Appraisal Sign-off)
- v4.3.0 — Goals, Appraisals, Skills Matrix
- v4.2.0 — Reports page, Supplier management
- v4.1.x — Vercel deploy, Supabase integration, mobile responsive, Supabase schema v2

---

## Rules (Always Follow)
- **After every major feature: update the Help page** at `bzhub_web/bzhub_web/src/app/help/page.tsx`

---

## Session Opener Template
1. "Read chat_persistent_notes/NOTES.md first."
2. State goal for this session (e.g. "Let's do FEAT-036 Supabase Auth")
3. Any constraints (design, tech, deadlines)
4. Any errors or blockers
