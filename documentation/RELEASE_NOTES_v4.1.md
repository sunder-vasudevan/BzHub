# BzHub v4.1.0 — Release Notes

## v5.1.0 — POS Overhaul + Bug Fixes
**Date:** 2026-03-17

### New Features
- **POS — Working Checkout**: creates Supabase sale records and deducts inventory per line item on checkout
- **POS — Qty Controls**: `−`/`+` buttons in cart per line item; capped to available stock
- **POS — Payment Method**: Cash / Card / UPI selector in cart panel, recorded on receipt
- **POS — Receipt Modal**: post-checkout itemized receipt with total, payment method, and print button
- **POS — Stock Validation**: product cards show "Out of Stock" overlay; disabled when unavailable; cart prevents adding beyond stock

### Bug Fixes
- **Version number** unified to `v5.0.0` across login page, sidebar footer, and help page
- **Currency reactivity**: changing currency in Settings now updates all pages instantly (no reload required) via `bzhub_currency_changed` event
- **Company name in sidebar**: company name saved to `localStorage` on Settings load/save; displayed as subtitle under BzHub logo in sidebar; updates live

### Architecture
- `src/hooks/useCurrency.ts` — now event-driven; listens for `bzhub_currency_changed`
- `src/app/settings/page.tsx` — dispatches `bzhub_currency_changed` and `bzhub_company_changed` events on save; caches company name to `localStorage`
- `src/components/layout/Sidebar.tsx` — reads `bzhub_company_name` from `localStorage`; updates reactively
- `src/app/operations/page.tsx` — POSTab fully rewired with checkout, receipt, stock controls

---

## v5.0.0 — Custom Fields Builder (FEAT-041 Phase 2.5a)
**Date:** 2026-03-13

### New Features
- **Settings → Custom Fields** — define extra fields for Employee, Contact, Lead, or Product entities
- Supported field types: Text, Number, Date, Yes/No, Dropdown, Email, Phone, URL
- Dropdown fields support configurable options list
- Field definitions stored in `localStorage` (`bzhub_custom_fields`) — no DB schema change required
- **Employee form** now renders custom fields automatically (both Add and Edit dialogs)
- Custom field values persist to Supabase `custom_data` table (JSONB); gracefully silenced if table not yet created
- **`CustomFieldRenderer` component** — generic component reusable across all entity forms
- SQL migration provided: `migrations/001_custom_data.sql` — run in Supabase SQL editor to activate value persistence

### Architecture
- `src/lib/customFields.ts` — NEW: types, localStorage helpers, `labelToId()`
- `src/components/CustomFieldRenderer.tsx` — NEW: renders form inputs from schema
- `src/lib/db.ts` — `fetchCustomData()`, `upsertCustomData()`; `createEmployee()` now returns inserted ID
- `src/app/settings/page.tsx` — Custom Fields card with entity tabs and field builder UI
- `src/app/hr/page.tsx` — Employee form wired to custom fields + custom data
- `migrations/001_custom_data.sql` — NEW

### Action Required
Run `migrations/001_custom_data.sql` in Supabase SQL editor to enable custom field value storage.

---

## v4.9.2 — Smart Insights Grouped by Category
**Date:** 2026-03-12

### Improvements
- Smart Insights card now groups alerts into: **Inventory**, **HR**, **Operations**, **Sales**
- Each group has its own icon, colour, and section header
- No cap on total insights — all surface within their category
- Warnings (amber dot) visually distinguished from info (grey dot) within each group

### Files Changed
- `src/lib/db.ts` — `group` field added to `Insight` interface and all `insights.push()` calls
- `src/app/dashboard/page.tsx` — grouped grid rendering (2-column on sm+)

---

## v4.9.1 — CRM View Switcher (List / Kanban / Funnel)
**Date:** 2026-03-12

### New Features
- **List view** — table with inline stage selector (default)
- **Kanban view** — restored column board with per-column Add Lead button
- **Funnel view** — horizontal bars per stage showing lead count + value; expandable rows; Won/Lost as outcome cards
- View persisted to `localStorage` (`bzhub_crm_view`)
- 3-button toggle in CRM header using List / LayoutGrid / Filter icons

### Files Changed
- `src/app/crm/page.tsx` — full rewrite with `ViewBtn`, `KanbanView`, `FunnelView` components

---

## v4.9.0 — CRM Table View with Inline Stage Selector
**Date:** 2026-03-12

### Changes
- Replaced Kanban board with a table view as default CRM layout
- Stage changes via inline `<select>` dropdown — no modal needed for quick moves
- Stage filter pills above table
- Pencil icon opens full edit modal
- Add Lead button in header (stage selectable in modal)

---

## v4.8.0 — Smart Insights Dashboard Card
**Date:** 2026-03-12

### New Features
- **FEAT-032a** — Smart Insights card on Dashboard (below KPI grid)
  - Stock depletion alerts: items with <7 days (warning) or <14 days (info) of stock remaining
  - HR nudges: pending appraisals, overdue goals
  - Approval nudges: pending leave requests, pending purchase orders
  - Sales anomaly: flags when this week's revenue is >20% below 3-week average
- All computed client-side from existing Supabase data — no external AI calls
- Collapsible card; only renders when there are insights
- `fetchInsights()` added to `src/lib/db.ts`

---

## v4.7.1 — Dynamic Brand Color
**Date:** 2026-03-12

### New Features
- Entire app color scheme changes when an industry template is selected in Settings
- CSS custom properties `--brand-color` / `--brand-color-hover` set on `document.documentElement`
- `initBrandColor()` called in `AppLayout` on mount for SSR-safe hydration
- 14 files updated: all hardcoded `#6D28D9` replaced with `var(--brand-color)`
- Defaults added to `globals.css` `:root`

### Files Changed
- `src/lib/templates.ts` — `applyTemplate()` and `initBrandColor()` set CSS vars
- `src/app/globals.css` — `:root` defaults
- `src/components/layout/AppLayout.tsx` — `initBrandColor()` on mount
- 11 page/component files — hardcoded color replaced

---

## v4.7.0 — Industry-Specific Templates
**Date:** 2026-03-12

### New Features
- **FEAT-038** — Industry-Specific Templates (Settings → Industry Template card)
  - 5 templates: General Business, Retail Store, Medical Clinic, Restaurant/F&B, Wholesale Distributor
  - Each template pre-configures dashboard KPI visibility for the industry type
  - Applying a template resets `bzhub_dashboard_prefs` in localStorage to industry-appropriate defaults
  - Active template shown with visual selection state (coloured border + checkmark)
  - Users can still customise KPIs further from Dashboard after applying a template

### Files Changed
- `src/lib/templates.ts` — new: template definitions, `getActiveTemplate()`, `applyTemplate()`
- `src/app/settings/page.tsx` — Industry Template card added
- `src/app/help/page.tsx` — Industry Templates help section added
- `documentation/FEATURE_SPECS.md` — new: detailed spec for all features
- `documentation/INTERACTION_LOG.md` — new: session tracking for efficiency analysis
- `documentation/BIZHUB_BUSINESS_DOCUMENT.md` — Section 5 and Roadmap updated to v4.7.0

---

## v4.6.0 — Notification Center, Dashboard Customization, CSV Export, Global Search, Audit Log
**Date:** 2026-03-12

### New Features
- **FEAT-021** — In-app Notification Center (bell icon, derives from existing data)
- **FEAT-023** — Customizable Dashboard (KPI card toggle, localStorage prefs)
- **FEAT-024** — CSV Export (Inventory, Employees, Reports tabs)
- **FEAT-025** — Global Search (Cmd+K modal, searches inventory/employees/contacts/leads)
- **FEAT-026** — Audit Log (/audit-log page, audit_logs Supabase table)

### Database
- New table: audit_logs (run documentation/supabase_schema_v3.sql)

### Files Changed
- src/lib/notifications.ts, src/lib/export.ts, src/components/GlobalSearch.tsx
- src/app/audit-log/page.tsx, src/components/layout/AppLayout.tsx
- src/components/layout/Sidebar.tsx, src/app/dashboard/page.tsx
- src/app/operations/page.tsx, src/app/hr/page.tsx, src/app/reports/page.tsx
- src/lib/db.ts, src/app/help/page.tsx, documentation/supabase_schema_v3.sql


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
