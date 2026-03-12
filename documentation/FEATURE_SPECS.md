# BzHub — Feature Specifications

Detailed specifications for every feature in BzHub — what it does, why it exists, what it does NOT do, and how it fits the product vision.

**Last Updated:** 2026-03-12 | **Current Version:** v4.6.0

---

## How to Use This Document
- Every feature shipped or planned gets a full spec entry here.
- Entries feed into the Business Document, pitch deck, and user guides.
- "Does NOT do" sections prevent scope creep and set honest expectations.

---

## Completed Features (Web App — v4.1 onwards)

---

### FEAT-021 — In-App Notification Center
**Version:** v4.6.0 | **Status:** Done

**What it does:**
A bell icon in the top navigation bar shows a badge count of unread notifications. Clicking opens a dropdown panel listing recent alerts derived from existing app data — low stock warnings, pending approvals, new leads in the pipeline, upcoming leave requests. Notifications are generated in real time from Supabase data, not a separate queue.

**User value:**
Managers get a single place to see what needs attention without checking every module. Reduces missed alerts and keeps the app feel "live."

**What it does NOT do:**
- Does not push browser notifications or mobile push alerts (WhatsApp/SMS is FEAT-033)
- Does not have user-configurable notification rules (future)
- Does not persist read/unread state in the database (localStorage only)

**Key files:** `src/lib/notifications.ts`, `src/components/layout/AppLayout.tsx`

---

### FEAT-023 — Customizable Dashboard
**Version:** v4.6.0 | **Status:** Done

**What it does:**
Users can toggle which KPI cards appear on the dashboard via a "Customize" button. Preferences are saved to localStorage and persist across sessions. The 6 KPI cards available are: Today's Sales, Inventory Value, Low Stock Count, Avg Daily Sales, Pipeline Value, and Growth (7-day). A trend chart time range (7 / 30 / 90 days) is also user-selectable.

**User value:**
A clinic owner does not need "Pipeline Value" on their dashboard. A distributor does not need "Low Stock Count." Customization makes the dashboard feel purpose-built rather than generic.

**What it does NOT do:**
- Does not support custom KPI formulas or new KPI cards (future AI feature)
- Does not sync preferences to Supabase (localStorage only — per device)
- Does not support layout rearrangement (drag-and-drop is future)

**Key files:** `src/app/dashboard/page.tsx`

---

### FEAT-024 — CSV Export
**Version:** v4.6.0 | **Status:** Done

**What it does:**
Export buttons on the Inventory, Employees, and Reports tabs download data as a `.csv` file directly in the browser. No server involvement — data fetched from Supabase is serialized client-side. File name includes the module and date.

**User value:**
Business owners regularly need data in Excel for accountants, auditors, or their own analysis. CSV export removes the need to manually copy-paste from screen.

**What it does NOT do:**
- Does not export to PDF or Excel (`.xlsx`) format
- Does not support custom column selection
- Does not export transaction-level POS data (only inventory snapshot and employee list)

**Key files:** `src/lib/export.ts`

---

### FEAT-025 — Global Search
**Version:** v4.6.0 | **Status:** Done

**What it does:**
Cmd+K (or Ctrl+K) opens a search modal that queries across Inventory items, Employees, CRM Contacts, and CRM Leads simultaneously. Results show name, type badge, and a direct link to the relevant module. Keyboard navigable (arrow keys, Enter).

**User value:**
In a multi-module ERP, finding "Rajesh Kumar" (who might be an employee, a contact, or a lead) requires checking three different pages. Global search collapses that into one keystroke.

**What it does NOT do:**
- Does not search Bills, Purchase Orders, or Audit Log entries
- Does not support fuzzy matching (exact substring match only)
- Does not index file attachments or note content

**Key files:** `src/components/GlobalSearch.tsx`

---

### FEAT-026 — Audit Log
**Version:** v4.6.0 | **Status:** Done

**What it does:**
Every significant create/update/delete action across the app writes a record to the `audit_logs` Supabase table: who did it, what entity, what action, and when. The `/audit-log` page shows a paginated, filterable table of all audit events. Useful for compliance, dispute resolution, and security review.

**User value:**
"Who deleted that inventory item?" becomes answerable. Critical for businesses with multiple staff users and for meeting compliance requirements.

**What it does NOT do:**
- Does not record field-level diffs (before/after values) — only action type
- Does not have user-level filtering in the UI (all users see all logs — RBAC is FEAT-022)
- Does not have automated log retention/purge policy

**Database:** `audit_logs` table (run `documentation/supabase_schema_v3.sql`)
**Key files:** `src/app/audit-log/page.tsx`

---

### FEAT-034 — Approval Workflows
**Version:** v4.4.0 | **Status:** Done

**What it does:**
Three approval workflows added across the app:

1. **Leave Requests (HR)** — Employees submit leave requests (Annual, Sick, Unpaid, Other) with date range and reason. Managers see pending requests with one-click Approve/Reject. Pending count shown on the Leave tab header.

2. **Purchase Orders (Operations)** — Create POs linked to existing suppliers. Full status workflow: Draft → Pending → Approved → Ordered → Delivered (or Rejected). Pending approval count shown in tab header.

3. **Appraisal Sign-Off (HR)** — Appraisals in Pending or In Progress state show Approve/Reject buttons. Adds Approved/Rejected status alongside the existing Completed status.

**User value:**
Formalises key business decisions that were previously informal (WhatsApp messages, verbal). Creates an auditable paper trail for HR and procurement decisions.

**What it does NOT do:**
- Does not support multi-level approvals (e.g., manager approves then director countersigns)
- Does not send email/WhatsApp notifications on status change (FEAT-033)
- Does not support approval delegation

**Database:** `leave_requests`, `purchase_orders` tables
**Key files:** `src/app/hr/page.tsx`, `src/app/operations/page.tsx`, `src/lib/db.ts`

---

### FEAT-035 — Employee Self-Service Portal
**Version:** v4.5.0 | **Status:** Done

**What it does:**
A dedicated `/employee-portal` page accessible from the sidebar. An employee selects their name from a dropdown (auth-ready: name picker swaps for auto-detected logged-in user when FEAT-036 ships). Four self-service tabs:

1. **My Goals** — View all assigned goals with status, target date, and check-in history
2. **My Appraisals** — View appraisal cycles; submit self-rating (0–5 stars) and self-comments for Pending or In Progress cycles
3. **My Leave** — View personal leave request history; submit new leave requests
4. **My Skills** — Read-only view of skills profile grouped by category with proficiency level

**User value:**
Employees can manage their own HR record without manager involvement for routine self-service tasks. Reduces HR admin overhead significantly.

**What it does NOT do:**
- Does not allow employees to edit their own profile (name, salary, role) — admin-only
- Does not have a mobile app or separate employee login (uses same web app, auth is FEAT-036)
- Does not show payslips or salary breakdown

**Key files:** `src/app/employee-portal/page.tsx`

---

### FEAT-038 — Industry-Specific Templates
**Version:** v4.7.0 (in progress) | **Status:** In Progress

**What it does:**
A template selector on the Settings page lets users pick from 5 industry pre-configurations. Each template sets dashboard KPI defaults optimised for that industry type. Applying a template:
1. Sets `bzhub_template` in localStorage
2. Resets dashboard KPI visibility to industry-appropriate defaults
3. Shows active template with a visual "selected" state in the Settings card

**Available templates:**

| Template | Best For | KPIs Adjusted |
|---|---|---|
| General Business | Any SMB (default) | All KPIs visible |
| Retail Store | Shops, e-commerce | Pipeline Value hidden by default |
| Medical Clinic | Clinics, health practices | Pipeline Value + Low Stock hidden |
| Restaurant / F&B | Cafes, restaurants, delivery | Pipeline Value hidden |
| Wholesale Distributor | B2B distributors, trading | All KPIs visible, CRM-forward |

**User value:**
First-time users see a dashboard that makes sense for their business immediately. A clinic owner doesn't see "Pipeline Value" — a metric meaningless to them. Removes onboarding friction and makes BzHub feel purpose-built for each industry.

**What it does NOT do:**
- Does not hide or show sidebar modules (all modules remain accessible — phase 2)
- Does not seed sample/demo data for the industry
- Does not require a database change (localStorage only)
- Does not lock users to an industry — they can switch templates any time

**Key files:** `src/lib/templates.ts`, `src/app/settings/page.tsx`

---

## Planned Features (Detailed)

---

### FEAT-039 — Offline-First Mode
**Priority:** Phase 2 | **Status:** Planned

**What it should do:**
Core operations (inventory lookups, POS transactions, employee check) work without internet connectivity. Changes are queued locally and synced to Supabase on reconnect. A connection status indicator shows online/offline state.

**Why it matters:**
Indian SMEs frequently experience unreliable internet. A POS that fails during a power cut or network outage loses customer trust immediately. Offline-first is table stakes for emerging market deployments.

**Technical approach:**
- Service Worker + IndexedDB for local data storage
- Sync queue with conflict resolution (last-write-wins for most entities, manual merge for inventory conflicts)
- Supabase Realtime for live sync when online

**Does NOT do:**
- Full offline for all 8 modules in v1 (prioritise Inventory + POS first)
- Real-time multi-user conflict resolution (too complex for Phase 2)

---

### FEAT-040 — GST / Tax Compliance (India)
**Priority:** Phase 2 | **Status:** Planned

**What it should do:**
GST-compliant invoicing with GSTIN fields, HSN/SAC codes, and automatic GST calculation (CGST + SGST for intra-state, IGST for inter-state). One-click GSTR-1 export (B2B, B2C summary in government-specified format). Tax rate management (0%, 5%, 12%, 18%, 28%).

**Why it matters:**
Every registered Indian business must file GST returns monthly. Currently BzHub has no GST fields — making it unusable for formal invoicing in India. This single feature unlocks the entire formal SME segment that was blocked by compliance requirements. It directly competes with Tally's core value prop.

**Does NOT do:**
- GSTR-3B auto-computation (complex reconciliation — future)
- E-way bill generation (logistics module — future)
- TDS/TCS computation

---

### FEAT-032 — AI-Powered Insights
**Priority:** Phase 2 | **Status:** Planned

**What it should do:**
- **Stock forecasting:** Predict which items will run out based on sales velocity trends
- **HR nudges:** Surface employees with no check-ins in 30 days, overdue appraisals
- **Sales anomaly detection:** Flag days/weeks with unusual sales patterns
- **Natural language queries:** "How many units of Product X did we sell last month?" answered inline

**Why it matters:**
The data is already in Supabase — the value is in surfacing it intelligently. Most SMB owners don't have time to run reports. Proactive AI insights that appear on the dashboard turn BzHub from a data repository into a business advisor.

**Technical approach:**
- Claude API for NL query processing
- Client-side trend analysis for stock forecasting (no external API needed)
- Threshold-based anomaly detection for sales

---

### FEAT-036 — Supabase Auth (Real Login)
**Priority:** Phase 3 | **Status:** Planned | **Blocker for multi-tenancy**

**What it should do:**
Replace the hardcoded `admin/admin123` login with real Supabase Auth. Email+password authentication with email verification. Session management via Supabase JWT. Password reset flow. "Remember me" option.

**Why it matters:**
Without real auth, BzHub cannot be deployed as a multi-user SaaS. Every company using it shares the same data. This is the single most important architectural blocker for commercialisation.

**Does NOT do:**
- Social login (Google, Microsoft) in Phase 1
- SSO/SAML (enterprise feature, Phase 4)
- Biometric/passkey auth

---

### FEAT-022 — RBAC (Role-Based Access Control)
**Priority:** Phase 3 | **Status:** Planned | **Depends on:** FEAT-036

**What it should do:**
Three roles: Admin, Manager, Employee. Role gates at the page and component level. Admins can manage all data. Managers can approve workflows but not change system settings. Employees can only access Employee Portal.

**Does NOT do:**
- Custom role creation (Admin-defined permission sets) — Phase 4
- Field-level permissions

---

### FEAT-037 — Multi-Tenancy
**Priority:** Phase 3 | **Status:** Planned | **Depends on:** FEAT-036

**What it should do:**
Each organisation gets an isolated data environment via `organization_id` on all Supabase tables + Row Level Security policies scoped to org. A single Supabase database serves all tenants with complete data isolation.

**Why it matters:**
This is the architectural prerequisite for SaaS — without it, BzHub can only serve one company at a time.

**Technical approach:**
- Add `organization_id` to all tables
- Update all RLS policies to `auth.uid() = org_members.user_id AND org_members.org_id = organization_id`
- Onboarding flow creates org → invites first admin user

---

### FEAT-033 — WhatsApp / SMS Integration
**Priority:** Phase 4 (Crown Jewel) | **Status:** Planned

**What it should do:**
- Send invoice payment links via WhatsApp
- Low-stock and reorder alerts via WhatsApp
- Leave approval notifications to manager via WhatsApp
- Run basic operations via WhatsApp commands ("stock PRODUCTNAME" → returns current stock level)

**Why it matters:**
India's business communication runs on WhatsApp. A system that sends alerts and accepts commands via WhatsApp is not a feature — it is a fundamental UX shift. This is the primary differentiation against Tally, Zoho, and every desktop ERP.

**Technical approach:**
- WhatsApp Business API (Meta) or Twilio WhatsApp sandbox
- Webhook to receive messages → parse commands → query Supabase → reply
- Phone number linked to company settings

---

## Feature Groups by Module

### Operations Module
| Feature | Status | Version |
|---|---|---|
| Inventory CRUD | Done | v4.1 |
| Point of Sale | Done | v4.1 |
| Bills History | Done | v4.1 |
| Supplier Management | Done | v4.2 |
| Purchase Orders + Approvals | Done | v4.4 |

### HR Module
| Feature | Status | Version |
|---|---|---|
| Employee Management | Done | v4.1 |
| Payroll Tracking | Done | v4.1 |
| Goals & Check-ins | Done | v4.3 |
| Appraisals + Sign-off | Done | v4.3/4.4 |
| Skills Matrix | Done | v4.3 |
| Leave Requests + Approvals | Done | v4.4 |
| Employee Self-Service Portal | Done | v4.5 |

### CRM Module
| Feature | Status | Version |
|---|---|---|
| Contacts Directory | Done | v4.1 |
| Leads Management | Done | v4.1 |
| Kanban Pipeline | Done | v4.1 |

### Dashboard & Analytics
| Feature | Status | Version |
|---|---|---|
| KPI Cards (6 metrics) | Done | v4.1 |
| Sales Trend Chart | Done | v4.1 |
| Fast/Slow Movers | Done | v4.1 |
| Customizable KPI Visibility | Done | v4.6 |
| Industry Templates | In Progress | v4.7 |

### Platform
| Feature | Status | Version |
|---|---|---|
| Vercel Deployment | Done | v4.1 |
| Supabase Integration | Done | v4.1 |
| Mobile Responsive | Done | v4.1.1 |
| Reports + CSV Export | Done | v4.2/4.6 |
| In-App Help | Done | v4.2.1 |
| Notification Center | Done | v4.6 |
| Global Search | Done | v4.6 |
| Audit Log | Done | v4.6 |

---

*See also: `RELEASE_NOTES_v4.1.md` for version-by-version changelog, `FEATURE_REQUESTS_AND_BUGS.md` for backlog status.*
