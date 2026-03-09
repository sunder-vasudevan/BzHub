# BizHub Code Review & Recommendations
**Reviewed:** 2026-03-09
**Reviewer:** Claude Code
**Codebase Version:** Desktop MVP (dev branch)

---

## Summary

The architecture is sound. The main pain points are a monolithic UI file, a few critical bugs, and missing safety rails (logging, error handling, DB indexes). No full rewrite needed — targeted fixes will have high impact.

**Overall rating:** Solid MVP. Ready for incremental improvement.

---

## Critical Issues (Fix Before Adding Features)

### 1. Inventory Not Decremented on POS Sale — DATA BUG
- **File:** `src/ui/desktop/bizhub_desktop.py` → `checkout_pos()`
- **Problem:** When a sale is completed, inventory quantity is never decremented in the database. Only the sales record is written.
- **Fix:** After `pos_service.record_sale()`, call `inventory_service.update_item(name, quantity=current - sold)`
- **Impact:** Data integrity — stock levels are wrong after every sale

### 2. SQL Injection Risk
- **File:** `src/db/sqlite_adapter.py`, lines ~441 and ~653
- **Problem:** Dynamic SQL built via string concatenation in `update_inventory_item()` and `update_employee()`
- **Fix:** Separate the column names (safe, hardcoded) from values (parameterized) — already partially done, needs audit
- **Impact:** Security vulnerability

### 3. Hardcoded Credentials
- **File:** `src/config.py`
- **Problem:** `ADMIN_USERNAME = 'admin'`, `ADMIN_PASSWORD = 'admin123'` in plaintext
- **Fix:** Move to environment variables or first-run setup flow
- **Impact:** Security — anyone with file access has admin login

---

## High Priority

### 4. Split bizhub_desktop.py (3,307 lines, 142 methods)
- **Problem:** One class does everything — UI layout, event handling, business logic, state management
- **Proposed structure:**
  ```
  src/ui/desktop/
  ├── bizhub_desktop.py       (app shell, login, nav — ~400 lines)
  └── tabs/
      ├── dashboard_tab.py
      ├── inventory_tab.py
      ├── pos_tab.py
      ├── hr_tab.py
      ├── visitors_tab.py
      ├── settings_tab.py
      └── crm_tab.py          (future real CRM)
  ```
- **Approach:** Each tab as a class with `__init__(parent, services, colors)` — no full rewrite, just extraction
- **Effort:** 3–5 days
- **Impact:** Enables adding CRM and other features without making the monolith worse

### 5. Replace print() with logging
- **Problem:** 20+ `print("[DEBUG]...")` statements throughout the codebase — not filterable, not structured
- **Fix:**
  ```python
  import logging
  logger = logging.getLogger(__name__)
  logger.debug("...")  # replaces print("[DEBUG]...")
  ```
- **Effort:** 1 day
- **Impact:** Production-ready diagnostics, filterable log levels

### 6. Add Database Indexes
- **File:** `src/db/sqlite_adapter.py` → `_initialize_db()`
- **Missing indexes:**
  ```sql
  CREATE INDEX IF NOT EXISTS idx_inventory_name ON inventory(item_name);
  CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(sale_date);
  CREATE INDEX IF NOT EXISTS idx_employees_number ON employees(emp_number);
  CREATE INDEX IF NOT EXISTS idx_visitors_date ON visitors(visit_date);
  ```
- **Effort:** 1 hour
- **Impact:** 10–100x faster queries as data grows

### 7. Database Connection Pooling / Context Manager
- **Problem:** Every method in `sqlite_adapter.py` opens and closes a new SQLite connection (~50+ patterns)
- **Fix:** Add a `_get_connection()` context manager:
  ```python
  from contextlib import contextmanager

  @contextmanager
  def _get_conn(self):
      conn = sqlite3.connect(self.db_file)
      try:
          yield conn
          conn.commit()
      except Exception:
          conn.rollback()
          raise
      finally:
          conn.close()
  ```
- **Effort:** 1–2 days (refactor all methods to use it)
- **Impact:** Cleaner code, proper rollback on errors, ~30% less boilerplate

---

## Medium Priority

### 8. Error Handling Framework
- **Problem:** Most service calls in the UI have no try/except — any DB error crashes silently or shows a traceback
- **Fix:**
  - Create custom exceptions: `InventoryError`, `AuthError`, `SaleError`
  - Wrap service calls in UI with try/except + user-facing messagebox
  - Add error logging at the service layer
- **Effort:** 2 days

### 9. Centralize UI State Management
- **Problem:** State scattered across 30+ instance variables (`self.pos_cart`, `self.current_role`, `self.crm_tab_index`, etc.)
- **Fix:** Create a `UIState` dataclass or simple dict with clear lifecycle (reset on logout)
- **Effort:** 2 days
- **Impact:** Fewer "destroyed widget" bugs, easier to debug

### 10. Service Layer: Add Value or Remove
- **Problem:** Most services are 30–60 line pass-throughs with no logic (e.g., `return self.db.get_all_items()`)
- **Decision needed:** Either add caching/validation to services, or remove the layer and call DB directly
- **Recommendation:** Keep services but add: input validation, caching for read-heavy calls, and better error wrapping
- **Effort:** 2–3 days

### 11. Add DB Constraints
- **Problem:** SQLite tables have no CHECK, UNIQUE, or NOT NULL constraints beyond primary keys
- **Fix:** Add constraints to schema in `_initialize_db()`:
  ```sql
  quantity INTEGER NOT NULL DEFAULT 0 CHECK(quantity >= 0),
  sale_price REAL NOT NULL CHECK(sale_price >= 0)
  ```
- **Effort:** 1 day
- **Impact:** Prevent invalid data at DB level

---

## CRM: Build from Scratch

The current "CRM" tab is just a wrapper around Inventory/POS/Visitors — no real CRM exists.

### What needs to be built:
1. **Contacts/Customers** — customer profiles distinct from Visitors
2. **Leads & Opportunities** — pipeline stages, lead source, expected value
3. **Pipeline / Kanban view** — drag cards between stages
4. **Follow-up tasks** — schedule calls, emails, reminders per lead
5. **Activity log** — notes and communication history per customer

### New DB tables needed:
```sql
CREATE TABLE contacts (id, name, company, phone, email, source, created_at);
CREATE TABLE leads (id, contact_id, title, stage, value, probability, owner, created_at);
CREATE TABLE lead_activities (id, lead_id, type, note, due_date, done, created_at);
```

### New service needed:
- `src/services/crm_service.py`

### Suggested build order:
1. DB schema + CRM service
2. Contacts list (simple table, CRUD)
3. Leads list with stage column
4. Kanban board view (pipeline)
5. Lead detail form with activity log

---

## Lower Priority / Future

- **Keyboard shortcuts** (`Ctrl+N` new, `Ctrl+S` save, `Esc` cancel) — 2 days
- **Caching** for inventory and employee lists — 2 days
- **Supabase migration** — use existing `DatabaseAdapter` abstraction, write `SupabaseAdapter`
- **HR gaps** — 360-degree feedback UI, goals tracking in UI
- **Reports drill-down** — click a KPI to see underlying transactions
- **Backup/restore** — scheduled SQLite backup to file
- **User management UI** — add/edit users from Settings tab (currently hardcoded)

---

## Effort Summary

| Task | Effort | Priority |
|------|--------|----------|
| Fix inventory decrement bug | 2 hours | Critical |
| Fix SQL injection | 1 day | Critical |
| Remove hardcoded creds | 2 hours | Critical |
| Add logging | 1 day | High |
| Add DB indexes | 1 hour | High |
| DB connection context manager | 1–2 days | High |
| Split bizhub_desktop.py | 3–5 days | High |
| Error handling framework | 2 days | Medium |
| UI state centralization | 2 days | Medium |
| Service layer improvements | 2–3 days | Medium |
| Build CRM from scratch | 2–4 weeks | High (feature) |

**Recommended sequence:**
Critical bugs → Logging → DB indexes → Split monolith → Build CRM

---

## Files to Touch (Reference)

| File | What to change |
|------|---------------|
| `src/db/sqlite_adapter.py` | Connection pooling, indexes, SQL injection fix, constraints |
| `src/ui/desktop/bizhub_desktop.py` | Split into tabs/, fix inventory bug, replace prints |
| `src/config.py` | Remove hardcoded creds |
| `src/services/` (all) | Add error handling, improve validation |
| `src/services/crm_service.py` | Create new |
| `src/db/base.py` | Add CRM abstract methods |

---

*Last updated: 2026-03-09*
