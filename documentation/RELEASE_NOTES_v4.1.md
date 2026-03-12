# BzHub v4.1.0 — Release Notes

## v4.5.0 — Employee Self-Service Portal
**Date:** 2026-03-12

### New Features
- **Employee Self-Service Portal** — new "My Portal" page in sidebar (`/employee-portal`)
  - Employee selects their name from a dropdown (auth-ready: name picker swaps for logged-in user when FEAT-036 ships)
  - **My Goals** — view all assigned goals with status and due dates
  - **My Appraisals** — view appraisal history; submit self-rating (0–5) and comments for Pending/In Progress cycles
  - **My Leave** — view own leave request history; submit new leave requests (Annual, Sick, Unpaid, Other)
  - **My Skills** — read-only view of skills profile grouped by category with proficiency levels

### Files Changed
- `src/app/employee-portal/page.tsx` — new page (created)
- `src/components/layout/Sidebar.tsx` — added "My Portal" nav item (UserCheck icon)
- `src/app/help/page.tsx` — help section for Employee Self-Service Portal

---

## v4.4.0 — Approval Workflows
**Date:** 2026-03-12

### New Features
- **Leave Requests** — new Leave tab in HR module
  - Employees submit leave requests (Annual, Sick, Unpaid, Other) with date range and reason
  - Manager approves or rejects directly from the table with one click
  - Pending count shown in tab header
- **Purchase Orders** — new Purchase Orders tab in Operations module
  - Create POs linked to existing suppliers with order/delivery dates and total amount
  - Full approval workflow: Pending → Approved → Ordered → Delivered (or Rejected)
  - Pending approval count shown in tab header
- **Appraisal Sign-Off** — Approve/Reject buttons added to Appraisals tab
  - Pending and In Progress appraisals show inline Approve/Reject actions
  - New statuses: Approved, Rejected (in addition to existing Pending/In Progress/Completed)

### Database
- New Supabase tables (run `documentation/supabase_schema_v2.sql` additions):
  - `leave_requests` — employee leave requests with status and review tracking
  - `purchase_orders` — POs linked to suppliers with approval workflow

### Files Changed
- `src/app/hr/page.tsx` — LeaveTab added, Appraisals sign-off buttons
- `src/app/operations/page.tsx` — PurchaseOrdersTab added
- `src/lib/db.ts` — LeaveRequest + PurchaseOrder types and CRUD functions
- `src/app/help/page.tsx` — Help sections for all 3 new features
- `documentation/supabase_schema_v2.sql` — new tables appended

---
**Date:** 2026-03-11
**Status:** Stable — Live on Vercel + Supabase

---

## v4.3.0 — HR Expansion: Goals, Appraisals & Skills
**Date:** 2026-03-11

### New Features
- **Goals & Check-ins** — set employee performance goals and log progress check-ins
- **Appraisals** — self and manager ratings with comments, period-based review cycles
- **Skills catalogue** — global skill library with category grouping
- **Employee Skills** — assign skills with proficiency levels to individual employees

### Database
- Supabase schema v2 additions at `documentation/supabase_schema_v2.sql`
  - New tables: `suppliers`, `goals`, `goal_checkins`, `appraisals`, `skills`, `employee_skills`
  - All tables use `bigserial primary key`, RLS enabled with open policies

---

## v4.2.0 — Reports & Supplier Management
**Date:** 2026-03-11

### New Features
- **Reports page** (`/reports`) — 3-tab reports module:
  - Sales Report — monthly aggregate table (revenue, # sales, avg order value)
  - Top Sellers — bar chart of top 10 products by quantity sold
  - Inventory Report — full stock table with value calculation and low-stock badges
- **Supplier Management** — new Suppliers tab in Operations:
  - Full CRUD: add, edit, delete suppliers
  - Fields: name, contact person, phone, email, notes
- **Sidebar** — Reports nav item added (BarChart3 icon)

### Files Changed
- `src/app/reports/page.tsx` — new Reports page
- `src/app/operations/page.tsx` — Suppliers tab added
- `src/components/layout/Sidebar.tsx` — Reports nav link
- `src/lib/db.ts` — supplier CRUD functions

---

## v4.1.2 — Vercel Build Fix
**Date:** 2026-03-11

### Fixes
- **`next.config.ts` → `next.config.js`** — Next.js 14 does not support TypeScript config file; replaced with `.js` to fix Vercel build failure
- **Excluded `resume_customizer_app/`** from BzHub git repo via `.gitignore` — was a nested git repo causing Vercel submodule warning and build instability

---

## What's New in v4.1

### Hosting
- **Deployed to Vercel** — app is live and publicly accessible
- **Supabase** replaces local SQLite as the cloud database
- Auto-deploy on every `git push origin main`

### Data Layer
- **`src/lib/supabase.ts`** — Supabase client initialisation
- **`src/lib/db.ts`** — full data layer replacing FastAPI calls:
  - Inventory CRUD
  - Sales fetch/create
  - CRM contacts + leads + pipeline
  - Employees + payroll
  - Company settings (upsert)
  - Dashboard KPIs, trend, product velocity — all computed client-side from Supabase
  - Hardcoded `login()` (admin/admin123) — Supabase Auth coming in next release
- All pages switched from `@/lib/api` → `@/lib/db`

### Database
- **Supabase schema** created (`documentation/supabase_schema.sql`)
  - Tables: inventory, sales, crm_contacts, crm_leads, crm_activities, employees, payroll, company_info
  - Row Level Security enabled with open policies (tighten with auth later)
- **Migration script** (`scripts/migrate_to_supabase.py`)
  - Migrated 33 inventory items, 24 sales, 20 employees from SQLite → Supabase

### Dev / Ops
- `start.sh` updated to use `.venv/bin/python` (fixes wrong interpreter bug)
- `vercel.json` added for Vercel build config
- `.env.local` holds Supabase keys (gitignored)
- Prompts log maintained at `memory/prompts_log.md`

---

## v4.1.1 — Mobile & Tablet Support
**Date:** 2026-03-11

### Responsive Layout
- **Mobile top bar** — hamburger menu + BzHub logo, visible only on phones/tablets
- **Sidebar** — hidden off-screen on mobile by default, slides in on hamburger tap, overlay closes it
- **Page padding** — reduced on mobile (`px-4 py-4`) vs desktop (`px-6 py-8`) across all pages

### Pages Updated
- **Operations** — inventory table scrolls horizontally, POS stacks vertically on mobile, item form single column on mobile
- **HR** — employee + payroll tables scroll horizontally, employee form single column on mobile
- **CRM** — tighter padding (Kanban already had horizontal scroll)
- **Dashboard** — tighter padding on mobile

### Files Changed
- `src/components/layout/AppLayout.tsx`
- `src/components/layout/Sidebar.tsx`
- `src/app/dashboard/page.tsx`
- `src/app/operations/page.tsx`
- `src/app/hr/page.tsx`
- `src/app/crm/page.tsx`

---

## Previous Releases
- v4.0.0 — Image upload, sortable tables, fast/slow movers dashboard, isolated bill print
- v3.1.0 — CRM Kanban, lead scoring, follow-ups
- v3.0 — Odoo-inspired CRM features
- v2.0 — Web frontend (Next.js + shadcn/ui) introduced
- v1.0.0 — Initial desktop app release
