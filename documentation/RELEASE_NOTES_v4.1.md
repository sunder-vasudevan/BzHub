# BzHub v4.1.0 — Release Notes
**Date:** 2026-03-11
**Status:** Stable — Live on Vercel + Supabase

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
