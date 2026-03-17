### FEAT-2026-UI-STATE — Refactor UI State Management for Stability
- **Date:** 2026-02-18
- **Area:** Desktop UI, Navigation, Tab/Widget Management
- **Status:** Open
- **Priority:** High
- **Summary:**
  - Refactor the UI state management to prevent errors when widgets (notebooks, frames, etc.) are destroyed and recreated.
  - Ensure all widget references are updated after UI resets (login/logout, navigation, etc.).
  - Add existence checks (`winfo_exists()`) before using widgets in event handlers.
  - Centralize UI clearing and rebuilding logic.
  - Decouple business logic from UI code where possible.
  - Add automated tests for navigation, login/logout, and tab switching.
- **Rationale:**
  - Prevents bugs where destroyed widgets are accessed, which break stable features when new features are added.
  - Makes the app more robust and maintainable as it grows.
- **Reference:** See recent bug with sidebar/tab switching and notebook destruction.
# BizHub Feature Requests & Bug Tracker

Single source of truth for new feature requests, bugs, and follow-up items.

## How to Use
- Add every new request/bug here first.
- Keep status updated (`Open`, `Planned`, `In Progress`, `Blocked`, `Done`).
- Add date and owner when known.
- Link code/docs/PRs where applicable.

---

## Open Bugs

### BUG-001 — Zoomed chart x-axis missing
- **Date:** 2026-02-04
- **Area:** Dashboard/Reports charts
- **Status:** Done
- **Priority:** Medium
- **Summary:** After double-clicking to zoom a chart, x-axis labels do not appear.
- **Steps:**
  1. Open Dashboard or Reports
  2. Double-click any chart to open zoom view
  3. Observe x-axis labels missing
- **Expected:** X-axis labels visible in zoom view
- **Actual:** X-axis labels not visible
- **Reference:** [documentation/BUGS.md](documentation/BUGS.md)
- **Work Started:** 2026-02-15
- **Implementation Notes:** Applied chart rendering/resizing changes in [src/ui/desktop/bizhub_desktop.py](src/ui/desktop/bizhub_desktop.py) to force visible x-tick labels, preserve rotation, and reserve bottom padding in zoomed charts.
- **Validation Update (2026-02-15):** User reported x-axis still missing after double-click zoom. Added second-pass fix: sparse date ticks + explicit subplot margins (removed tight-layout clipping behavior).
- **Validation Update (2026-02-15, pass 3):** User reported x/y tick fonts too large and x-axis still missing. Added third-pass fix: reduced tick font scaling, shorter date labels (`MM-DD`), explicit axis labels, and fallback zero-data trend axis to keep x-axis visible.
- **Validation Update (2026-02-15, pass 4):** Fonts confirmed fixed; x-axis still missing in zoom. Added deterministic axis rendering with fixed locator/formatter, forced bottom ticks/labels visibility, explicit x-limits, and increased bottom subplot margin.
- **Validation Result (2026-02-15):** User confirmed issue appears fixed and working fine.

---

## Feature Requests (Backlog)

### FEAT-XXX — Refactor app for better management
- **Status:** Open
- **Date:** 2026-02-16
- **Area:** Architecture/Maintainability
- **Priority:** High
- **Summary:** Refactor the BizHub app to improve maintainability, modularity, and scalability. Adopt a clearer separation of concerns, improve error handling, and make it easier to add new features.
- **Rationale:**
  - Current codebase is monolithic in places, with UI and business logic mixed.
  - Refactoring will make the app easier to maintain, test, and extend.
- **Suggested Steps:**
  1. Modularize features (inventory, POS, HR, etc.) into separate classes/files.
  2. Move business logic to service classes, keep UI code focused on presentation.
  3. Consider adopting MVC or MVVM pattern for separation of concerns.
  4. Centralize error handling and configuration management.
  5. Add/expand unit and integration tests.
  6. Update documentation to reflect new structure.
- **Owner:** Unassigned

### FEAT-021 — Notification Center
- **Status:** Done v4.6.0
- **Priority:** Medium
- **Target Phase:** UI/Product
- **Summary:** In-app notifications for important events (e.g., sales targets, low inventory, new messages).

### FEAT-022 — User Roles & Permissions
- **Status:** Open
- **Priority:** High
- **Target Phase:** Security/Product
- **Summary:** Multi-user support with role-based access control for different modules.

### FEAT-023 — Customizable Dashboard
- **Status:** Done v4.6.0
- **Priority:** Medium
- **Target Phase:** UI/Product
- **Summary:** Allow users to personalize dashboard widgets and analytics cards.

### FEAT-024 — Export/Import Data
- **Status:** Done v4.6.0
- **Priority:** Medium
- **Target Phase:** Product Features
- **Summary:** Enable exporting reports to Excel/PDF and importing data from CSV.

### FEAT-025 — Advanced Search & Filters
- **Status:** Done v4.6.0
- **Priority:** Medium
- **Target Phase:** UI/Product
- **Summary:** Add global search and advanced filtering for transactions, inventory, and contacts.

### FEAT-026 — Audit Log
- **Status:** Done v4.6.0
- **Priority:** Medium
- **Target Phase:** Security/Product
- **Summary:** Track user actions and changes for security and compliance.

### FEAT-038 — Industry-Specific Templates
- **Status:** Done v4.7.0
- **Priority:** High
- **Target Phase:** Phase 2 — USP / Differentiation
- **Summary:** One-click industry setup for Retail, Clinic, Restaurant, and Wholesale Distributor. Applies dashboard KPI defaults and pre-configuration optimised for each industry type.
- **What it does:**
  - Template selector card on Settings page with 5 options: General, Retail, Clinic, Restaurant, Distributor
  - Each template sets which dashboard KPI cards are visible by default
  - Stored in localStorage (`bzhub_template`) — no DB change required
  - Applying a template resets dashboard prefs to industry defaults; user can still customise further
- **What it does NOT do:**
  - Does not hide/show sidebar modules (Phase 2 enhancement)
  - Does not seed sample data
  - Does not require Supabase schema change
- **Key files:** `src/lib/templates.ts` (new), `src/app/settings/page.tsx`, `src/app/help/page.tsx`
- **Full spec:** See `documentation/FEATURE_SPECS.md`

### FEAT-039 — Offline-First Mode
- **Status:** Planned
- **Priority:** High
- **Target Phase:** Phase 2 — USP / Differentiation
- **Summary:** Core operations (Inventory, POS) work without internet connectivity. Changes queue locally and sync to Supabase on reconnect. Critical for Indian SME market with unreliable connectivity.

### FEAT-040 — GST / Tax Compliance (India)
- **Status:** Planned
- **Priority:** High
- **Target Phase:** Phase 2 — USP / Differentiation
- **Summary:** GST-compliant invoicing with GSTIN, HSN/SAC codes, CGST/SGST/IGST calculation. GSTR-1 export. Directly competes with Tally's primary value proposition.

### FEAT-032 — AI-Powered Insights
- **Status:** Planned
- **Priority:** Medium
- **Target Phase:** Phase 2 — USP / Differentiation
- **Summary:** Stock forecasting, HR nudges, sales anomaly detection, and natural language queries powered by Claude API.

### FEAT-027 — Quick Add/Shortcut Bar
- **Status:** Open
- **Priority:** Low
- **Target Phase:** UI/Product
- **Summary:** Add a floating bar for rapid access to frequent actions (e.g., add sale, new customer).

### FEAT-028 — Theming & Accessibility
- **Status:** Open
- **Priority:** Medium
- **Target Phase:** UI Modernization
- **Summary:** More color themes, font size options, and accessibility improvements.

### FEAT-029 — Integration with External Services
- **Status:** Open
- **Priority:** Medium
- **Target Phase:** Product Features
- **Summary:** Connect with external services (e.g., email, calendar, accounting software).

### FEAT-030 — Performance Analytics & ML
- **Status:** Open
- **Priority:** Medium
- **Target Phase:** Product Features
- **Summary:** Deeper analytics, trend predictions, and anomaly detection using basic ML.
### FEAT-001 — Modern Tkinter themes
- **Status:** Planned
- **Priority:** Medium
- **Target Phase:** UI Modernization

### FEAT-002 — Dashboard analytics
- **Status:** Done
- **Priority:** High
- **Target Phase:** UI/Product
- **Work Started:** 2026-02-15
- **Implementation Notes:** Added advanced KPI metrics in [src/ui/desktop/bizhub_desktop.py](src/ui/desktop/bizhub_desktop.py): `Avg Daily Sales` and `Sales Growth %` (period-over-period).
- **Validation Result (2026-02-15):** User confirmed KPI cards are working fine.

### FEAT-003 — Charts and graphs enhancements
- **Status:** Done
- **Priority:** Medium
- **Target Phase:** UI/Product
- **Work Started:** 2026-02-15
- **Implementation Notes:** Enhanced chart readability in [src/ui/desktop/bizhub_desktop.py](src/ui/desktop/bizhub_desktop.py) with data point markers, grid lines, and value labels.
- **Validation Result (2026-02-15):** User confirmed chart updates working fine.

### FEAT-004 — Dark mode support
- **Status:** Done
- **Priority:** Medium
- **Target Phase:** UI Modernization
- **Work Started:** 2026-02-15
- **Implementation Notes:** Added persisted UI preference for dark mode in [src/ui/desktop/bizhub_desktop.py](src/ui/desktop/bizhub_desktop.py) using [assets/ui_preferences.json](assets/ui_preferences.json).
- **Validation Result (2026-02-15):** User confirmed feature working.

### FEAT-005 — Responsive desktop layout improvements
- **Status:** In Progress
- **Priority:** Medium
- **Target Phase:** UI Modernization
- **Work Started:** 2026-02-15
- **Implementation Notes:** Added auto-responsive sidebar behavior in [src/ui/desktop/bizhub_desktop.py](src/ui/desktop/bizhub_desktop.py): compact mode under narrower widths with dynamic quick-action labels and compact settings button.
- **Validation Update (2026-02-15):** User reported hidden icons when reducing width. Added top-nav compact mode (icon-only nav/help/dark-mode labels), hid username at very small widths, and increased compact sidebar width.

### FEAT-006 — Customer loyalty system
- **Status:** Planned
- **Priority:** Medium
- **Target Phase:** Product Features

### FEAT-007 — Supplier management
- **Status:** Planned
- **Priority:** Medium

### FEAT-008 — Authentication/User Management Model Review
- **Status:** Planned
- **Priority:** High
- **Target Phase:** Supabase Integration / User Management
- **Work Started:** 2026-02-16
- **Description:** Re-evaluate the authentication and user management approach for BizHub. Current Supabase model requires email-based sign-up and confirmation, which may not fit all use cases (e.g., admin-driven user creation, non-email users, or custom login flows). Consider supporting admin login, custom user management, or alternative authentication flows if Supabase's default is too restrictive.
- **Target Phase:** Product Features

### FEAT-008 — Advanced reporting
- **Status:** Planned
- **Priority:** High
- **Target Phase:** Product Features

### FEAT-009 — Inventory forecasting
- **Status:** Planned
- **Priority:** High
- **Target Phase:** Product Features

### FEAT-010 — Multi-location support
- **Status:** Planned
- **Priority:** High
- **Target Phase:** Product Features

### FEAT-011 — REST API (FastAPI)
- **Status:** Planned
- **Priority:** High
- **Target Phase:** Web Interface

### FEAT-012 — Web UI (Flask + Vue)
- **Status:** Planned
- **Priority:** Medium
- **Target Phase:** Web Interface

### FEAT-013 — Mobile-responsive design
- **Status:** Planned
- **Priority:** Medium
- **Target Phase:** Web Interface

### FEAT-014 — Real-time notifications
- **Status:** Planned
- **Priority:** Medium
- **Target Phase:** Web Interface

### FEAT-015 — Cloud storage integration
- **Status:** Planned
- **Priority:** Medium
- **Target Phase:** Web/Cloud

### FEAT-016 — PostgreSQL adapter
- **Status:** Planned
- **Priority:** High
- **Target Phase:** Cloud Deployment

### FEAT-017 — Multi-tenant support
- **Status:** Planned
- **Priority:** High
- **Target Phase:** Cloud Deployment

### FEAT-018 — AWS/GCP deployment
- **Status:** Planned
- **Priority:** Medium
- **Target Phase:** Cloud Deployment

### FEAT-019 — Docker containerization
- **Status:** Planned
- **Priority:** Medium
- **Target Phase:** Cloud Deployment

### FEAT-020 — Performance optimization for cloud scale
- **Status:** Planned
- **Priority:** Medium
- **Target Phase:** Cloud Deployment

### FEAT-NEW — Web Compatibility and Central Database
- **Status:** Open
- **Date:** 2026-02-18
- **Area:** Architecture/Deployment
- **Summary:**
    1. Refactor UI and business logic for future web compatibility (fonts, UI, and flow should be easily portable to a web stack).
    2. Implement a central/shared database (e.g., PostgreSQL, MySQL, or cloud DB) to allow multiple desktop users to access and update data concurrently from different machines.
- **Notes:**
    - For now, focus is on desktop improvements.
    - Central database will require network configuration, user authentication, and possible migration from local SQLite.
    - Web compatibility will be planned after desktop refactor is stable.

### FEAT-NEW — Supabase Integration for BizHub
- **Status:** Planned
- **Date:** 2026-02-18
- **Area:** Database/Cloud
- **Summary:** Integrate BizHub desktop app with Supabase (PostgreSQL) for central, cloud-based data storage and multi-user access. Migrate from local SQLite to Supabase, update database adapters, and provide configuration for connection credentials.
- **Notes:**co
    - No data sharing with Ideaboard app required.
    - Focus on secure, reliable, and scalable setup for 2–3 desktop users.
    - To be implemented after UI refactor is complete.

### FEAT-SUPABASE — Complete Supabase Migration
- **Status:** Planned
- **Date:** 2026-02-18
- **Owner:** Copilot
- **Summary:** Migrate all remaining business logic (sales, HR, payroll, appraisals, analytics, etc.) to SupabaseService. Refactor/remove legacy service usages for these modules. Ensure all CRUD and reporting operations use Supabase. Test multi-user, multi-desktop scenarios for all modules.

### FEAT-031 — Workspace Reorganization
- **Status:** Open
- **Priority:** High
- **Target Phase:** Architecture/Maintainability
- **Summary:** Plan and execute a workspace reorganization to improve clarity, modularity, and maintainability. Move related files into appropriate folders (backend, frontend, shared, docs), update import paths, clean up duplicates/obsolete files, and document the new structure in the architecture file.
- **Rationale:**
  - Current workspace structure is sprawling and can be confusing.
  - A clear, modular structure will make onboarding, development, and deployment easier.
- **Suggested Steps:**
  1. Map current workspace and propose new structure.
  2. Move/categorize files and folders accordingly.
  3. Update all import paths and references.
  4. Remove or archive obsolete/duplicate files.
  5. Update documentation (ARCHITECTURE.md) to reflect changes.
- **Owner:** Unassigned

---

## In Progress
### FEAT-005: Responsive desktop layout improvements
Status: Done
Owner: Copilot
Description: Sidebar and top navigation remain usable and icons visible at all window sizes. Compact mode for sidebar/top-nav at small widths.
Validation Checklist:
  - [x] Sidebar compacts to icons-only at small widths
  - [x] Top navigation compacts to icons-only at small widths
  - [x] All icons remain visible and usable at all window sizes
  - [x] User validation after relaunch

Validation Log:
  - 2026-02-15: User reported icons hidden at small widths; further compact mode logic added.
  - 2026-02-15: User confirmed feature is working fine after relaunch.
- [x] Resize zoom window; confirm labels remain visible
- [x] Repeat in **CRM → Reports → Sales Trend** zoom

### B) FEAT-003 Validation — Chart readability enhancements
- [x] In Dashboard Sales Trend, confirm line markers are visible
- [x] Confirm y-grid lines are visible
- [x] Confirm latest point value label appears
- [x] In Top Selling Items chart, confirm x-grid lines are visible
- [x] Confirm each bar has a numeric value label
- [x] Repeat checks in Reports charts

### Validation Outcome
- **Status:** Passed (User confirmed)
- **If pass:** move BUG-001 and FEAT-003 to `Done`
- **If fail:** capture screenshot + exact path (Dashboard/Reports) + resize state

## Completed
- BUG-001 — Zoomed chart x-axis missing
- FEAT-003 — Charts and graphs enhancements
- FEAT-002 — Dashboard analytics
- FEAT-004 — Dark mode support

---

## References
- [documentation/REFACTORING_COMPLETE.md](documentation/REFACTORING_COMPLETE.md)
- [documentation/ARCHITECTURE.md](documentation/ARCHITECTURE.md)
- [documentation/REFACTORING_SUMMARY.md](documentation/REFACTORING_SUMMARY.md)
- [bizhub.py](bizhub.py)

---

**Created:** 2026-02-15
**Last Updated:** 2026-02-15

## 2026-02-18

### Features Added
- FastAPI backend modules for:
  - Inventory (/inventory)
  - HR (/hr/employees)
  - POS (/pos/transactions)
  - Visitor (/visitors)
- All modules fetch data directly from Supabase tables using supabase-py client.
- Supabase integration: credentials loaded from environment variables (SUPABASE_URL, SUPABASE_SERVICE_KEY).

### Bugs/Issues
- None reported for new modules as of this update.

++++this feature list was given by calude code on Feb 19------

Great question. Looking at what established ERPs like SAP, Odoo, QuickBooks, Zoho, and Tally offer, here's what could be added organized by module:

---

**Core Modules (most critical for small businesses)**

*Financial Management* — general ledger, chart of accounts, journal entries, bank reconciliation, multi-currency support, tax management (GST/VAT), financial statements (P&L, balance sheet, cash flow), budgeting and forecasting.

*Accounts Payable/Receivable* — vendor invoicing, payment scheduling, aging reports, credit limit management, automatic payment reminders, receipt matching.

*Inventory & Warehouse* — multi-location stock tracking, barcode/QR scanning, stock valuation methods (FIFO/LIFO/weighted avg), reorder point alerts, batch and serial number tracking, stock transfer between locations.

*Point of Sale (POS)* — billing counter UI, barcode scanning at checkout, receipt printing, cash drawer integration, daily sales summary.

---

**Business Operations**

*Purchase Management* — purchase orders, vendor comparison, goods received notes (GRN), purchase returns, vendor rating.

*Sales Management* — quotations → sales orders → invoices pipeline, delivery challan, sales returns, price lists, discount management.

*CRM* — lead and opportunity tracking, follow-up reminders, customer communication history, deal pipeline view.

*HR & Payroll* — employee profiles, attendance tracking, leave management, salary computation, payslip generation, statutory deductions (PF, ESI for India).

---

**Advanced Modules**

*Manufacturing* — bill of materials (BOM), work orders, production planning, raw material consumption tracking, finished goods output.

*Project Management* — project costing, task tracking, time logging, milestone billing.

*Asset Management* — fixed asset register, depreciation schedules, asset disposal tracking.

*E-commerce Integration* — sync inventory with Shopify/WooCommerce, auto-create sales orders from online purchases.

---

**Reporting & Intelligence**

- Dashboard with KPIs (revenue, expenses, stock value, outstanding receivables)
- Drill-down reports (click a number to see underlying transactions)
- Scheduled email reports
- Export to Excel/PDF
- Role-based report access

---

**Cross-Cutting Features**

- **Multi-user with role-based access control (RBAC)** — admin, accountant, salesperson, warehouse staff roles
- **Audit trail** — who changed what and when
- **Multi-branch/company support** — separate books per branch, consolidated view
- **Document attachment** — attach PDFs/images to invoices, POs, etc.
- **Notifications & alerts** — low stock, overdue payments, upcoming tax deadlines
- **Data import/export** — bulk import via CSV for products, customers, opening stock
- **Backup & restore** — scheduled DB backups, one-click restore

---

**Integrations worth planning for**

- Payment gateways (Razorpay, Stripe, PayPal)
- SMS/WhatsApp notifications for invoices and reminders
- Email (SMTP) for sending documents directly
- Tally XML import/export (very relevant for Indian businesses)
- GST filing integration (for India — GSTN API)
- Bank statement import (CSV/OFX for reconciliation)

---

**Suggested priority order for a small business ERP:**

1. Inventory + POS
2. Sales & Purchase orders
3. Accounting (AR/AP + GL)
4. Reporting dashboard
5. HR/Payroll
6. CRM
7. Manufacturing (if applicable)

The beauty of building your own is you can tailor this specifically to a niche — say, a retail shop, a clinic, or a small manufacturer — rather than trying to be everything at once like SAP does.

---

**The Tkinter Problem**

Tkinter looks dated by default — flat widgets, system fonts, no smooth animations, no shadows, no rounded corners natively. You can fight it with libraries like `ttkbootstrap` or `CustomTkinter`, but you're always patching around limitations.

---

**Option 1 — Stick with Tkinter but modernize it**

Use **CustomTkinter** — it's the best facelift available for Tkinter right now.

```bash
pip install customtkinter
```

What it gives you: rounded corners, dark/light mode, modern button styles, smooth-ish widgets. It's a drop-in replacement for most `ttk` widgets.

Also pair it with:
- **ttkbootstrap** for themed styling (Bootstrap-inspired)
- **Pillow** for image/icon rendering
- **matplotlib** embedded in frames for charts on dashboards

Realistically though, even with all of this, it'll look like a 2018 app at best.

---

**Option 2 — Switch to a Web-based UI (recommended)**

Since you already have `--web` planned in your CLI, this is the natural path. You write a Python backend and a proper frontend.

**Best stack for your use case:**

Backend: **FastAPI** — fast, modern, auto-generates API docs
Frontend: **React + Tailwind CSS** or just **plain HTML + HTMX** if you want to keep it simple

```
bizhub/
├── backend/         # FastAPI app
│   ├── routers/     # inventory, sales, accounts...
│   └── models/      # SQLAlchemy models
├── frontend/        # React or HTMX
└── bizhub.py        # your existing entry point
```

You'd open the app in a browser — but package it as a desktop app using **Electron** or **Tauri** so it still feels native.

---

**Option 3 — Best of Both Worlds: PyWebView**

This is underrated for exactly your use case.

```bash
pip install pywebview
```

You write your UI in HTML/CSS/JS (full modern web stack — Tailwind, animations, whatever), and PyWebView wraps it in a native desktop window with no browser chrome. To the user it looks and feels like a desktop app. Your Python backend handles all the logic.

```python
import webview

webview.create_window("BizHub", "frontend/index.html", js_api=my_api)
webview.start()
```

This is how many modern desktop ERPs are actually built today.

---

**UI Design Principles regardless of stack**

**Layout:**
- Sidebar navigation (not top tabs) — it scales better as you add modules
- Consistent 8px spacing grid
- Cards for dashboard metrics, not raw tables
- Breadcrumbs so users always know where they are

**Color & Typography:**
- One primary brand color, neutral grays for everything else
- Don't use more than 2 fonts — one for headings, one for body
- Red/green only for status indicators (not decorative)
- Sufficient contrast — WCAG AA minimum

**Tables (you'll have a lot of them):**
- Alternating row colors or subtle borders
- Sticky headers when scrolling
- Inline actions (edit/delete icons on hover) instead of separate pages
- Column sorting and filtering built in
- Pagination or virtual scrolling for large datasets

**Forms:**
- Inline validation, not after submit
- Logical tab order
- Autofocus on first field
- Keyboard shortcuts for power users (Ctrl+S to save, Esc to cancel)

**Feedback:**
- Toast notifications for success/error (not alert popups)
- Loading spinners for any operation over 300ms
- Confirmation dialogs only for destructive actions
- Empty states with helpful prompts (not just blank tables)

---

**Recommended path for your project specifically**

Given you're building a serious ERP:

1. Keep your existing Tkinter app as-is for now (it works)
2. Build the FastAPI backend in parallel
3. Create a simple React or HTMX frontend
4. Use **PyWebView** to wrap it as a desktop app
5. Gradually migrate features from Tkinter to the web UI

This way you always have a working app at every stage and end up with something that genuinely looks and feels modern — not just "modernized Tkinter."

A good free UI reference to study: **Odoo's web client** and **ERPNext** — both are open source ERPs with excellent UI you can draw inspiration from.

---

## Features to Add (Inspired by Odoo)

### 1. Multiple View Modes
Odoo's most powerful UI concept is **switching between views on the same data**. Every list of records should support:

- **List view** — sortable, filterable table with bulk actions
- **Kanban view** — drag-and-drop cards grouped by status (great for sales pipelines, tasks, purchase orders)
- **Form view** — single record detail with related tabs
- **Calendar view** — for appointments, deliveries, due dates
- **Dashboard/Graph view** — charts and KPIs for the same data

A customer list shouldn't just be a table. Users should be able to flip to Kanban to see customers grouped by segment, or a graph showing revenue by customer. Odoo puts a view switcher in the top right of every screen — steal this directly.

---

### 2. The Chatter / Activity Log
Odoo's chatter feature allows note and message translations, message pinning, and real-time collaboration. This is one of Odoo's most beloved features and almost no small business ERP copies it properly.

On every record (invoice, sale order, customer, product) add a **side panel** that contains:
- Internal notes (visible only to staff)
- Messages sent to the customer
- Automatic system logs ("Invoice confirmed by Ravi on Feb 19")
- Scheduled activities ("Follow up call on March 1 — assigned to Sales")
- File attachments linked to that specific record

This turns every record into a mini collaboration thread, eliminating external email chains.

---

### 3. Smart Search Bar
Odoo 17's new search view moved the search tab to the center, combining Filter, Group By, and Favorites into one unified location.

Your search should support:
- **Filters** — predefined (e.g., "Overdue invoices", "Low stock items")
- **Group By** — dynamically group any list by any field (by customer, by month, by category)
- **Favorites** — save your custom search+filter combination and recall it in one click
- **Full-text search** across all relevant fields, not just name

---

### 4. Breadcrumb Navigation with Back Stack
Odoo lets you drill down deep — Customer → Sales Orders → Invoice → Payment — and maintains a breadcrumb trail at the top so you can jump back to any level. This is critical for an ERP. Your current Tkinter app likely opens new windows; replace that with an in-place navigation stack.

---

### 5. Customizable Dashboard
Odoo 17 allows users to create blank dashboards from scratch and introduced dashboard sharing so users can share dashboards with clients or colleagues.

Build a dashboard where users can:
- Add/remove KPI tiles (Total Sales, Outstanding Receivables, Stock Value, etc.)
- Drag and rearrange widgets
- Choose chart types (bar, line, pie, gauge)
- Set date ranges (Today / This Month / This Quarter / Custom)
- Share a dashboard view with a team member or export as PDF

---

### 6. Keyboard Shortcuts & Power User Mode
Odoo 17 added fast record selection via keyboard and Shift key support for quick multi-select.

Add keyboard shortcuts throughout:
- `Alt+N` → New record
- `Alt+S` → Save
- `Esc` → Discard/go back
- `Ctrl+K` → Command palette (search any screen/action by name — like VS Code's Cmd+P)

The command palette is a game-changer for power users in a complex ERP.

---

### 7. Inline Editing in List View
Odoo lets you click a field in a list and edit it directly without opening the full form. This is huge for productivity — updating 10 product prices doesn't require 10 form opens. Implement this for key fields like price, quantity, status.

---

### 8. Dark Mode
One of the standout features of Odoo 17 is Dark Mode, which reduces eye strain during late-night work. This is now a user expectation, not a luxury. It also adds perceived quality to your app.

---

### 9. Draggable / Resizable Dialogs
In previous Odoo versions, pop-up dialogs were rigid and couldn't be moved. Odoo 17 changed this by allowing users to drag and reposition pop-ups. Small thing, massive UX improvement for users who need to reference data behind a dialog.

---

### 10. Progressive Web App (PWA)
Odoo's PWA features include offline access, push notifications, and shortcuts for quick app access. If you go the web route, packaging it as a PWA means users can install it on their desktop or phone from the browser — no app store needed.

---

## How to Actually Build This

### Recommended Stack

```
Frontend:   React + Tailwind CSS
Backend:    FastAPI (Python)
Database:   SQLite (dev) → PostgreSQL (prod)
Desktop:    PyWebView (wraps the web app in a native window)
Charts:     Recharts or Apache ECharts
Icons:      Lucide or Heroicons
```

This mirrors how Odoo itself works — Odoo uses OWL (Odoo Web Library), a modern component-based JavaScript framework with reactive state management — similar in concept to React and Vue but optimized for Odoo. You don't need to use OWL, but React gives you the same component model.

---

### UI Structure to Copy from Odoo

```
┌─────────────────────────────────────────────────────┐
│  [Logo]  [App Switcher ▼]          [Search    ] [👤] │  ← Top bar
├──────────┬──────────────────────────────────────────┤
│          │  Customers                    [List][Kanban] │
│ SALES    │  ┌─────────────────────────────────────┐ │
│  Customers│  │ Filter ▼  Group By ▼  Favorites ▼  │ │  ← Smart search
│  Orders  │  └─────────────────────────────────────┘ │
│          │  ☐  Name        Phone     Balance  Status │
│ PURCHASE │  ☐  Ravi Kumar  99999...  ₹12,000  Active│
│  ...     │  ☐  Tech Corp   88888...  ₹ 5,000  Active│
│          │                                           │
│ ACCOUNTS │                           [1-80 of 240 >]│
│  ...     │                                           │
└──────────┴──────────────────────────────────────────┘
```

Key things to notice:
- **App switcher** in the top bar (like Odoo's grid icon) to jump between modules
- **Sidebar** shows module sections, collapsible
- **View toggle** top right of every list
- **Smart search bar** always visible above data
- **Pagination** bottom right

---

### Color System to Use

Odoo 17 uses a clean neutral palette with one brand accent. Here's a practical system you can adopt directly:

```css
--primary:     #714B67;   /* Odoo's signature purple — or use your own */
--bg:          #F9FAFB;   /* Page background */
--surface:     #FFFFFF;   /* Cards, forms */
--border:      #E5E7EB;   /* Subtle borders */
--text-main:   #111827;   /* Headings */
--text-muted:  #6B7280;   /* Labels, hints */
--success:     #22C55E;
--danger:      #EF4444;
--warning:     #F59E0B;
```

---

### Practical Implementation Roadmap

**Phase 1 — Foundation (2-3 weeks)**
Set up FastAPI backend + React frontend + PyWebView shell. Get one module (Inventory) working end-to-end with List + Form views.

**Phase 2 — Core UX Patterns (2 weeks)**
Build the reusable components: SmartTable (sortable, filterable, paginated), FormView, KanbanBoard, SearchBar, Toast notifications, BreadcrumbNav.

**Phase 3 — Dashboard (1 week)**
Build the home dashboard with draggable KPI cards and basic charts using ECharts.

**Phase 4 — Chatter & Activities (1 week)**
Add the activity/notes panel to all major records. This single feature will make your app feel enterprise-grade.

**Phase 5 — Polish (ongoing)**
Dark mode, keyboard shortcuts, command palette, PWA manifest, loading skeletons instead of spinners.

---

The key insight from Odoo is that it's not about having 100 features — it's about having **consistent UI patterns** that work the same way across every module. Once a user learns how to search, filter, and navigate in one module, they instantly know how to use every other module. That consistency is what makes it feel professional.

---

## CLI & App Entry Point Features (bizhub.py)

- Unified entry point for all app modes (desktop, web, API, future extensions)
- Command-line argument parsing for flexible launch (desktop, web, API, DB selection, version info)
- Default to robust desktop (Tkinter) mode with clear error handling
- Modular import of UI/app logic (separation of concerns)
- Future-ready: placeholders for web and API server modes
- Configurable database file path for easy environment switching
- Graceful error reporting and exit codes
- Usage documentation embedded in script docstring
- Clean main() function for maintainability and testability
- Follows best practices for Python CLI apps (argparse, __main__ guard, sys.path management)

---

## Implementation Roadmap & Solution Plan

### Phase 1: Complete Desktop ERP Core
- Finish advanced features in Inventory, POS, HR, CRM (batch/serial, Kanban, inline edit, activity log)
- Add power-user features: keyboard shortcuts, breadcrumbs, customizable dashboard

### Phase 2: Web/API Foundation
- Scaffold FastAPI backend and basic web UI (React or HTMX)
- Implement one module (Inventory) end-to-end

### Phase 3: Cloud & Multi-user
- Migrate to central DB (Supabase/PostgreSQL)
- Add multi-user, RBAC, and audit trail

### Phase 4: Advanced Modules & Integrations
- Add accounting, AR/AP, manufacturing, project, and asset modules
- Integrate with email, payment gateways, and external services

### Phase 5: Polish & Consistency
- Implement Odoo-inspired UI patterns everywhere
- Add PWA support, dark mode polish, and full documentation

---

## Module-by-Module Gap Analysis (as of Feb 2026)

- **CLI & App Entry:** 100% complete (robust, modular, future-ready)
- **Desktop UI (Tkinter):** ~80% (core tabs, themes, responsive; needs advanced UI/UX, power features)
- **ERP Modules:** Inventory, POS, HR, CRM ~60–70% (core flows present, advanced features pending); Accounting, Manufacturing, Project, Asset, E-commerce 0–10% (not yet implemented)
- **Web/API Modes:** 0% (placeholders only)
- **Cloud/Database/Integration:** 10–20% (Supabase planned, groundwork in place)
- **Reporting & Intelligence:** ~50% (dashboard, analytics exist; advanced drill-down, scheduled reports pending)
- **UI/UX Consistency & Power Features:** ~40% (some modern patterns, Odoo-style navigation and features pending)

---

## Progress Estimate (Feb 2026)

- Core CLI/desktop foundation: 90–100% complete
- ERP module implementation: 60–70%
- Web/API and advanced extensibility: 0–10%
- Overall toward full feature list: **65–70%**

---

## Next Steps
- Prioritize modules for MVP
- Create or update tickets for each actionable feature
- Begin implementation with the highest-priority module (e.g., Inventory)
- Track progress using this roadmap and update as features are completed

---

## Implementation Roadmap (Updated 2026-03-12)

> **Ultimate Goal:** WhatsApp-first operations + Multi-tenancy SaaS model. All features below should be built with this end-state in mind — e.g. notifications should be extensible to WhatsApp, data models should be org-aware from the start.

### Priority Order
1. ~~FEAT-034 — Approval Workflows~~ ✅ Done v4.4.0
2. ~~FEAT-035 — Employee Self-Service Portal~~ ✅ Done v4.5.0
3. FEAT-021 — In-app Notification Center ← NEXT
4. FEAT-023 — Customizable Dashboard
5. FEAT-024 — Export/Import (Excel/PDF/CSV)
6. FEAT-025 — Advanced Search & Filters
7. FEAT-026 — Audit Log
8. FEAT-038 — Industry-Specific Templates
9. FEAT-039 — Offline-First Mode
10. FEAT-040 — GST / Tax Compliance (India)
11. FEAT-036 — Supabase Auth *(enables multi-user)*
12. FEAT-037 — Multi-Tenancy *(SaaS enabler — depends on FEAT-036)*
13. FEAT-033 — WhatsApp / SMS *(final phase — the crown jewel)*

---

## USP & Differentiation Ideas (2026-03-12)

### FEAT-032 — AI-Powered Insights
- **Status:** Partial — FEAT-032a Done (v4.8.0 / v4.9.2), NL query parked Phase 4
- **Priority:** High
- **Target Phase:** Intelligence / Product Differentiation
- **Completed (v4.8.0 / v4.9.2):**
  - Smart Insights card on Dashboard — stock depletion forecasting, HR nudges (pending appraisals, overdue goals), approval nudges (leave/POs), sales anomaly detection
  - Grouped by category: Inventory, HR, Operations, Sales
  - All computed client-side from existing Supabase data
- **Remaining (Phase 4 — FEAT-032b):**
  - Natural language query: type "Show me sales vs last month" → chart (requires Claude API)
- **Rationale:** Most SMB ERPs show raw data — none proactively tell you what to do next. This is a clear USP.

---

### FEAT-033 — WhatsApp / SMS Notifications
- **Status:** Open
- **Priority:** High
- **Target Phase:** Integrations / Product Differentiation
- **Summary:** Send automated alerts and business notifications via WhatsApp and/or SMS.
  - Low stock alerts to purchase manager
  - Pending approval reminders (purchase orders, leave requests)
  - Goal deadline reminders to employees
  - Invoice payment reminders to customers
- **Implementation:** WhatsApp Business API (via Twilio or direct Meta API); SMS via Twilio/SNS.
- **Rationale:** Most SMBs already live in WhatsApp. Meeting them there is a massive UX advantage over email-only ERPs.

---

### FEAT-034 — Approval Workflows
- **Status:** Open
- **Priority:** Medium
- **Target Phase:** Operations
- **Summary:** Configurable multi-step approval flows for key business actions.
  - Purchase orders above a threshold require manager sign-off
  - Leave requests routed to line manager
  - Appraisals require both self-review and manager sign-off before closing
- **Rationale:** Prevents unauthorized spend and formalizes processes that SMBs currently handle informally via WhatsApp.

---

### FEAT-035 — Employee Self-Service Portal
- **Status:** ✅ Done v4.5.0 (2026-03-12)
- **Priority:** Medium
- **Target Phase:** HR / Product Differentiation
- **Summary:** Give employees their own login to view and interact with their own data.
  - View own goals and check-ins
  - Submit self-appraisal rating and comments
  - View own skill profile
  - Apply for leave
- **Dependency:** Requires FEAT-036 (Supabase Auth) first.

---

### FEAT-036 — Supabase Auth (Real Login System)
- **Status:** Open
- **Priority:** High (blocker for multi-tenancy and self-service)
- **Target Phase:** Security / Architecture
- **Summary:** Replace hardcoded `admin/admin123` login with proper Supabase Auth.
  - Email + password login via Supabase
  - Role-based access: Admin, Manager, Employee
  - Session management (JWT tokens, auto-refresh)
- **Rationale:** Required before any multi-user or multi-tenant features can be built.

---

### FEAT-037 — Multi-Tenancy (One App, Many Organisations)
- **Status:** Open
- **Priority:** High — Phase 2 (after core features)
- **Target Phase:** Architecture / Cloud
- **Summary:** Support multiple independent organisations in a single deployment, each with isolated data and their own logins.
- **Architecture:** Row-level multi-tenancy via Supabase RLS.
  - Add `organization_id` column to every table
  - RLS policies filter all queries by the authenticated user's org
  - `organizations` table + `user_organizations` junction table with roles
- **Onboarding flow:** Organisation signs up → gets their own org record → admin invites users → data is fully isolated from day one
- **Dependency:** Requires FEAT-036 (Supabase Auth) first.
- **Effort estimate:** ~3–4 days after auth is in place.
- **Rationale:** Enables the app to be sold as a SaaS product to multiple clients with zero infrastructure overhead per client.
- **Note:** This is the primary SaaS monetisation enabler — all data models being built now should keep `organization_id` in mind.

---

### FEAT-038 — Industry-Specific Templates
- **Status:** Open
- **Priority:** High
- **Target Phase:** Product Differentiation / Onboarding
- **Summary:** One-click setup for specific industries. When a new organisation is created, they choose their industry and the app pre-loads relevant defaults.
  - **Retail** — inventory categories (clothing, electronics, etc.), POS configured, sales reports
  - **Clinic** — patient records, appointment scheduling, billing
  - **Restaurant** — menu items, table management, kitchen order flow
  - **Distributor** — multi-location stock, purchase orders, route planning
- **Implementation:** Seed scripts per industry template, applied at org creation time (ties into FEAT-037 onboarding flow).
- **Rationale:** Odoo is too generic — industry-specific defaults reduce setup time from days to minutes. Faster time-to-value = better conversion and retention.

---

### FEAT-039 — Offline-First Mode
- **Status:** Open
- **Priority:** Low (deliberately deprioritized 2026-03-17 — moved to last in Phase 2 backlog)
- **Target Phase:** Architecture / Reliability
- **Summary:** App remains fully functional without internet connectivity and syncs data when reconnected.
  - Local IndexedDB or SQLite (via WASM) as offline store
  - Background sync queue for mutations made offline
  - Conflict resolution strategy (last-write-wins or manual merge)
  - Visual indicator showing online/offline/syncing state
- **Rationale:** Critical for SMBs in markets with unreliable connectivity (India, SE Asia, Africa). Competitors like Tally work offline natively — this is table stakes for that market.

---

### FEAT-041 — Customizable SaaS Platform (Custom Fields + Module Builder)
- **Status:** Partial Done — Phase 2.5a shipped (v5.0.0); 2.5b (Module Builder) and 2.5c (Nav Config) pending
- **Date:** 2026-03-13
- **Priority:** High
- **Target Phase:** Phase 2.5 — SaaS Extensibility
- **Summary:** Allow customers to extend BzHub without code — add custom fields to existing entities and build entirely new record-type modules via a schema UI. This is the foundation of the "customizable SaaS" architecture.

#### Problem It Solves
Every SMB has unique data needs. A clinic needs a "Referring Doctor" field on patients. A distributor needs a "Route" field on customers. Today they can't add these — BzHub is rigid. This feature makes BzHub extensible without requiring code or a developer.

#### What It Does NOT Do (Scope Boundary)
- No formula engine or computed fields (Phase 3+)
- No drag-and-drop workflow builder (Phase 4)
- No third-party plugin marketplace (Phase 5)
- No cross-module relational fields in V1

---

#### Architecture

**Supabase Schema (3 new tables):**

```sql
-- Defines custom fields attached to an entity type
entity_custom_fields (
  id uuid PRIMARY KEY,
  org_id uuid,            -- multi-tenant ready
  entity_type text,       -- 'employee' | 'contact' | 'lead' | 'product' | 'invoice'
  fields jsonb,           -- [{name, label, type, required, options[], order}]
  updated_at timestamptz
)

-- Defines entirely new custom modules (record types)
custom_modules (
  id uuid PRIMARY KEY,
  org_id uuid,
  slug text,              -- url-safe name, e.g. 'projects'
  label text,             -- display name, e.g. 'Projects'
  icon text,              -- lucide icon name
  schema jsonb,           -- same fields[] format as above
  nav_order int,          -- where it appears in sidebar
  created_at timestamptz
)

-- Stores records for custom modules
custom_records (
  id uuid PRIMARY KEY,
  org_id uuid,
  module_id uuid REFERENCES custom_modules(id),
  data jsonb,             -- {'field_name': value, ...}
  created_at timestamptz,
  updated_at timestamptz
)
```

**Supported Field Types (V1):**
`text` | `number` | `date` | `boolean` | `dropdown` (single select) | `multiselect` | `url` | `email` | `phone`

---

#### Feature Breakdown

**Part A — Custom Fields on Existing Entities**
- Settings → Custom Fields → pick entity type (Employee, Contact, Lead, Product, Supplier)
- Add/edit/remove fields: name, label, field type, required toggle, dropdown options
- Custom fields render automatically in: list table columns, detail/edit forms
- Stored on each record as `custom_data: jsonb` column (add to existing tables)
- GIN index on `custom_data` for query performance

**Part B — Custom Module Builder**
- Settings → Custom Modules → Create New Module
- Define: module name, icon, fields (same field type palette)
- BzHub auto-generates: sidebar nav item, list view table, create/edit form, record detail page
- All CRUD rendered dynamically from the schema JSON
- Module appears in sidebar under a "Custom" section

**Part C — Navigation Config**
- `org_nav_config` or extend Settings to store sidebar item order + visibility
- Admins can reorder, show/hide both built-in and custom modules
- Sidebar becomes config-driven (currently hardcoded)

---

#### Key Files to Create / Modify
| File | Change |
|---|---|
| `src/app/settings/page.tsx` | Add "Custom Fields" and "Custom Modules" tabs |
| `src/app/settings/custom-fields/page.tsx` | NEW — field builder UI per entity |
| `src/app/settings/custom-modules/page.tsx` | NEW — module schema builder UI |
| `src/app/custom/[slug]/page.tsx` | NEW — dynamic CRUD page rendered from schema |
| `src/lib/db.ts` | `fetchCustomModule()`, `fetchCustomRecords()`, `upsertCustomRecord()` |
| `src/components/layout/Sidebar.tsx` | Read nav config, render custom module items |
| `src/components/CustomFieldRenderer.tsx` | NEW — renders any field type from schema JSON |
| Supabase migrations | 3 new tables + `custom_data jsonb` on existing entity tables |

---

#### Phased Rollout
| Phase | Scope | Effort |
|---|---|---|
| **2.5a** | Custom fields on Employees + Contacts | ~1 session |
| **2.5b** | Custom Module Builder (full CRUD from schema) | ~2 sessions |
| **2.5c** | Nav config — reorder/hide sidebar items | ~0.5 session |
| **3.x** | Relational fields (link records across modules) | Phase 3 |
| **4.x** | Workflow automation on custom modules | Phase 4 |

**Recommended starting point:** Phase 2.5a — custom fields on Employees only. Prove the pattern, then extend.

---

#### Risks & Caveats
- `jsonb` search is slower than typed columns — mitigate with GIN indexes
- Schema changes (renaming/deleting fields) can orphan existing data — need migration UX
- Multi-tenancy must be enforced via `org_id` on every query (RLS policy required)
- This must be built **after FEAT-036 (Auth)** to have meaningful `org_id` — OR built with a single-org placeholder and migrated when auth lands

#### Dependency
- Soft dependency on **FEAT-036** (Supabase Auth) for true per-org isolation
- Can ship Phase 2.5a/b with single-org assumption, migrate to multi-org after FEAT-037

---

### FEAT-040 — GST / Tax Compliance (India)
- **Status:** Open
- **Priority:** High (if targeting India)
- **Target Phase:** Finance / Compliance
- **Summary:** Full GST-compliant invoicing and reporting built into the app.
  - GST invoice generation (CGST, SGST, IGST breakdown)
  - Auto-calculate GST based on HSN/SAC codes
  - GSTR-1 and GSTR-3B export (JSON/Excel format for filing)
  - Tax summary reports by period
  - Support for composition scheme and regular GST taxpayers
- **Rationale:** Tally dominates Indian SMB accounting solely because of GST compliance. BzHub can compete directly and offer a modern cloud alternative. This is a moat in the Indian market.

---

### FEAT-042 — Post-Sale Fulfillment Stages in CRM Pipeline
- **Status:** Open
- **Priority:** Medium
- **Target Phase:** CRM / Operations
- **Reference:** MassTech APMaldi Sales pipeline flow (v1.92) — `documentation/MassTech_Pipeline_Mapping.md`
- **Summary:** Extend the CRM pipeline beyond "Won" to include production and shipping fulfillment stages, enabling end-to-end deal tracking from first contact through delivery.
  - Add four post-sale stages: **In Production**, **Production Complete**, **Shipped**, **Closed Won**
  - "Won" becomes an intermediate stage (Sales Order Confirmed), not a terminal one
  - "Closed Won" becomes the new terminal success state
  - Kanban, List, and Funnel views updated to accommodate 10-stage pipeline
  - Post-sale stages visually separated from pre-sale stages (e.g. dashed divider or section header)
- **Proposed full stage sequence:**
  `New → Qualified → Proposal → PO Received → In Production → Production Complete → Shipped → Closed Won | Lost`
- **Rationale:** MassTech's operations show that deals don't end at "Won" — production, shipping, and delivery happen after the sale. Collapsing these into "Won" loses visibility over the fulfillment pipeline. This is relevant to any product-based business using BzHub.
- **Dependency:** Can be implemented standalone. Pairs well with FEAT-043 (auto/manual tagging) and FEAT-044 (team ownership).

---

### FEAT-043 — Auto vs. Manual Stage Transition Tagging
- **Status:** Open
- **Priority:** Low–Medium
- **Target Phase:** CRM / UX
- **Reference:** MassTech APMaldi Sales pipeline flow (v1.92) — `documentation/MassTech_Pipeline_Mapping.md`
- **Summary:** Allow each pipeline stage transition to be tagged as **Automatic** (triggered by a system event) or **Manual** (requires a human action), and surface this in the UI.
  - Stage config stores a `transition_type` field: `"auto"` or `"manual"`
  - Kanban column headers or stage badges display a small indicator (e.g. a lightning bolt for auto, a hand icon for manual)
  - Tooltip on the indicator explains the trigger condition (e.g. "Moves automatically when quote is sent")
  - Admin-configurable trigger labels per stage
- **Rationale:** In multi-step B2B pipelines, some stages advance automatically (e.g. when a quote is emailed) while others require deliberate action (e.g. receiving a PO). Surfacing this distinction reduces confusion and improves process adherence.
- **Dependency:** Builds on FEAT-042 (extended stages). Aligns with FEAT-041 (Custom Fields) if stage config is made schema-driven.

---

### FEAT-044 — Team Ownership per Pipeline Stage
- **Status:** Open
- **Priority:** Low–Medium
- **Target Phase:** CRM / HR Integration
- **Reference:** MassTech APMaldi Sales pipeline flow (v1.92) — `documentation/MassTech_Pipeline_Mapping.md`
- **Summary:** Assign a responsible team (or role) to each pipeline stage so it is clear who owns a deal at any point in the pipeline.
  - Stage config stores an `owner_team` field (e.g. "Marketing", "Production", "Shipping", "Support")
  - Team label shown on Kanban column headers and deal cards
  - Optional: filter pipeline view by team to show only the stages relevant to a given department
  - Optional: notify team members when a deal enters their stage (links to FEAT-021 Notification Center)
- **Rationale:** In MassTech's flow, responsibility shifts from Marketing (stages 1–5) to Production/Shipping (stages 6–9) mid-pipeline. Without explicit ownership, deals can stall at handoff points. Team tags make handoffs explicit and accountable.
- **Dependency:** Builds on FEAT-042 (extended stages). Optional integration with FEAT-021 (Notifications) and FEAT-022 (RBAC).

---

### FEAT-POS-V2 — POS Overhaul (v5.1.0)
- **Status:** ✅ Done (v5.1.0 — 2026-03-17)
- **Priority:** —
- **Summary:** Full POS rewrite from UI-only placeholder to working transaction system.
  - Working checkout: creates Supabase sale records + deducts inventory per line item
  - Qty controls (−/+) per cart line with stock cap
  - Payment method selector: Cash / Card / UPI
  - Receipt modal after checkout: itemized, total, print button
  - Out-of-stock overlay + disabled state on product cards
  - Inventory auto-reloads after checkout

### BUG-VERSION-SYNC — Version Number Mismatch (v5.1.0)
- **Status:** ✅ Fixed (v5.1.0 — 2026-03-17)
- **Summary:** Version displayed as v4.0 on login page, v4.0.0 in sidebar, v4.6 in help page. All unified to v5.0.0.

### BUG-CURRENCY-REACTIVITY — Currency Change Not Propagating (v5.1.0)
- **Status:** ✅ Fixed (v5.1.0 — 2026-03-17)
- **Summary:** Changing currency in Settings only took effect after full page reload. useCurrency hook now listens for bzhub_currency_changed event dispatched on save — all pages update instantly.

### BUG-COMPANY-NAME — Company Name Not Shown in Sidebar (v5.1.0)
- **Status:** ✅ Fixed (v5.1.0 — 2026-03-17)
- **Summary:** Company name set in Settings was never displayed in the sidebar logo. Now cached to localStorage on Settings load/save and shown as subtitle under BzHub in sidebar. Updates live via bzhub_company_changed event.

---
