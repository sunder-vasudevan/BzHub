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
# Bzhub Feature Requests & Bug Tracker

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
- **Summary:** Refactor the Bzhub app to improve maintainability, modularity, and scalability. Adopt a clearer separation of concerns, improve error handling, and make it easier to add new features.
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
- **Status:** Open
- **Priority:** Medium
- **Target Phase:** UI/Product
- **Summary:** In-app notifications for important events (e.g., sales targets, low inventory, new messages).

### FEAT-022 — User Roles & Permissions
- **Status:** Open
- **Priority:** High
- **Target Phase:** Security/Product
- **Summary:** Multi-user support with role-based access control for different modules.

### FEAT-023 — Customizable Dashboard
- **Status:** Open
- **Priority:** Medium
- **Target Phase:** UI/Product
- **Summary:** Allow users to personalize dashboard widgets and analytics cards.

### FEAT-024 — Export/Import Data
- **Status:** Open
- **Priority:** Medium
- **Target Phase:** Product Features
- **Summary:** Enable exporting reports to Excel/PDF and importing data from CSV.

### FEAT-025 — Advanced Search & Filters
- **Status:** Open
- **Priority:** Medium
- **Target Phase:** UI/Product
- **Summary:** Add global search and advanced filtering for transactions, inventory, and contacts.

### FEAT-026 — Audit Log
- **Status:** Open
- **Priority:** Medium
- **Target Phase:** Security/Product
- **Summary:** Track user actions and changes for security and compliance.

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
- **Description:** Re-evaluate the authentication and user management approach for Bzhub. Current Supabase model requires email-based sign-up and confirmation, which may not fit all use cases (e.g., admin-driven user creation, non-email users, or custom login flows). Consider supporting admin login, custom user management, or alternative authentication flows if Supabase's default is too restrictive.
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

### FEAT-NEW — Supabase Integration for Bzhub
- **Status:** Planned
- **Date:** 2026-02-18
- **Area:** Database/Cloud
- **Summary:** Integrate Bzhub desktop app with Supabase (PostgreSQL) for central, cloud-based data storage and multi-user access. Migrate from local SQLite to Supabase, update database adapters, and provide configuration for connection credentials.
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

webview.create_window("Bzhub", "frontend/index.html", js_api=my_api)
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

### FEAT-PR-AUTO — Automate PR Creation
- **Status:** Open
- **Priority:** Medium
- **Summary:** Add a script and workflow to automate the creation of GitHub pull requests after pushing a branch, reducing manual steps and ensuring consistent PR metadata.
- **Rationale:** Streamlines the development workflow, reduces errors, and saves time for contributors.
- **Implementation:**
  1. Provide a shell script (create_pr.sh) that pushes the current branch and opens a PR to the dev branch using GitHub CLI.
  2. Document usage examples in the README or developer guide.
  3. Optionally, extend with auto-labeling or auto-merge features via GitHub Actions.
- **Owner:** Copilot
