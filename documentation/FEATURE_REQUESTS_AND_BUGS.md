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
