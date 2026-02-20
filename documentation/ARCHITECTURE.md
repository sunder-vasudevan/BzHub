## Lead/Opportunity Module (CRM)

### Overview
The Lead/Opportunity module is the foundation of the CRM system, inspired by Odoo's best practices. It manages the full lifecycle of sales leads and opportunities, supporting advanced pipeline, scoring, and analytics features.

### Functional Scope
- Core CRUD for leads/opportunities (create, view, edit, delete, assign, stage tracking)
- Kanban pipeline for visual sales stage management (drag-and-drop, stage transitions)
- Lead/opportunity scoring and assignment logic (score calculation, auto-assignment, prioritization)
- Automated follow-up reminders and scheduled activities
- Email logging and tracking with CRM contacts and opportunities
- Lost reason analysis (capture and report on lost opportunities)
- Custom pipeline stages and tags for opportunities
- Geo-location/map view for leads/opportunities
- CRM-specific reporting/dashboard (pipeline metrics, analytics)

### Data Model (Key Fields)
- id (primary key)
- name (lead/opportunity title)
- contact_name, contact_email, contact_phone
- company
- stage (e.g., New, Qualified, Proposal, Won, Lost)
- value (potential deal value)
- source (website, referral, campaign, etc.)
- assigned_to (user id)
- status (active, archived)
- created_at, updated_at
- notes (text)
- tags (for custom pipeline stages/tags)
- score (for scoring logic)

### Implementation Roadmap
1. Lead/Opportunity CRUD (core data model and operations)
2. Kanban pipeline for CRM
3. Lead/opportunity scoring
4. Automated follow-ups
5. Email integration for CRM
6. Lost reason analysis
7. Custom stages/tags for CRM
8. Geo-location for leads/opportunities
9. CRM-specific reporting/dashboard

### Odoo-Inspired Features
- Kanban pipeline view for sales stages
- Lead scoring and auto-assignment
- Automated follow-ups and activities
- Email integration and logging
- Lost reason capture and analytics
- Customizable pipeline stages/tags
- Geo-location mapping
- CRM analytics dashboard

This modular approach allows incremental delivery and testing, with each sub-feature tracked in FEATURES_BUGS_ISSUES.csv for visibility and progress.
# BizHub - Cloud-Ready ERP Suite Architecture

## 2026 Web & Cloud Architecture Update

**Frontend:** Next.js (TypeScript) app in `bzhub_web/` (deployed on Vercel)
**Backend API:** FastAPI app in `api/` (deployed on Render)
**Database:** Supabase (managed Postgres, auth, storage)

All major design choices and future decisions will be documented in this file. Please update this document with every significant architectural or technology decision.

**Version:** 1.0.0  
**Status:** Refactored with cloud-ready, modular architecture

## Overview

BizHub is a complete ERP solution for small businesses. The codebase has been refactored into a **cloud-ready, modular architecture** designed for:

- ✅ **Desktop deployment** (Tkinter - works offline)
- 🔮 **Web deployment** (Flask/FastAPI - future)
- 🔮 **Cloud database** (PostgreSQL/MySQL - future)
- ✅ **API-first** design for extensibility

## Architecture

```
bizhub/
├── src/
│   ├── core/                    # Pure business logic (no DB/UI dependencies)
│   │   └── __init__.py         # Calculators: Password, Currency, Inventory, POS, HR, Bill
│   │
│   ├── db/                      # Abstract database layer (swap backends easily)
│   │   ├── base.py             # Abstract DatabaseAdapter interface
│   │   ├── sqlite_adapter.py   # SQLite implementation (current)
│   │   └── __init__.py
│   │
│   ├── services/                # High-level business operations
│   │   ├── auth_service.py     # User authentication
│   │   ├── inventory_service.py
│   │   ├── pos_service.py      # Point of Sale
│   │   ├── hr_service.py       # Human Resources
│   │   ├── visitor_service.py
│   │   ├── email_service.py
│   │   ├── misc_service.py     # Activity logging, company info
│   │   └── __init__.py
│   │
│   ├── ui/
│   │   ├── desktop/
│   │   │   ├── bizhub_desktop.py    # Tkinter desktop app
│   │   │   └── __init__.py
│   │   └── web/                     # (Legacy) Flask/Vue.js web UI (see bzhub_web/ for Next.js)
├── bzhub_web/                  # Next.js (TypeScript) frontend (Vercel)
│   │
│   ├── config.py               # Environment-based configuration
│   └── __init__.py
│
├── api/                        # REST API layer (FastAPI, Render)
│   ├── app.py                 # FastAPI server
│   └── __init__.py
│
├── tests/
│   ├── test_bizhub_refactored.py    # Service & core logic tests
│   └── conftest.py
│
├── bizhub.py                   # Main launcher script
├── requirements.txt            # Dependencies
├── setup.py                    # Package metadata
└── README.md
```

## Key Design Principles

### 1. **Separation of Concerns**

- **`core/`** = Pure Python business logic
  - No database calls
  - No UI dependencies
  - 100% testable without mocking
  - Example: `InventoryCalculator.calculate_inventory_value()`

- **`db/`** = Data persistence abstraction
  - `base.py`: Abstract interface defines all operations
  - `sqlite_adapter.py`: SQLite implementation
  - Future: `postgres_adapter.py`, `mysql_adapter.py`

- **`services/`** = Business orchestration
  - Uses `db` for persistence
  - Uses `core` for calculations
  - Example: `InventoryService.get_inventory_value()` calls both

- **`ui/`** = User interface layer
  - Uses `services` only (never direct DB calls)
  - Can be swapped (Tkinter → Flask → React)

### 2. **Database Abstraction**

Switch databases without changing business logic:

```python
# desktop mode: SQLite
db = SQLiteAdapter('inventory.db')

# cloud mode (future): PostgreSQL
db = PostgreSQLAdapter(os.getenv('DB_URL'))

# Same services work with both!
inventory = InventoryService(db)
items = inventory.get_low_stock_items()  # Works the same
```

### 3. **Configuration-Driven**

Environment variables control everything:

```bash
# Desktop mode (default)
python bizhub.py

# Cloud mode (future)
DB_TYPE=postgresql DB_URL=postgresql://user:pass@host/db python bizhub_api.py

# Web mode (future)
MODE=web python bizhub.py --web
```

### 4. **Core Logic Independence**

Business calculations have zero dependencies:

```python
from src.core import POSCalculator

# This works anywhere, no database needed!
total = 100.0
discounted = POSCalculator.apply_discount(total, 10.0)
with_tax = POSCalculator.apply_tax(discounted, 18.0)
print(with_tax)  # 98.2
```

## Running the Application

### Desktop (Tkinter)

```bash
python bizhub.py
```

Credentials:
- Username: `admin`
- Password: `admin123`

### Testing

```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_bizhub_refactored.py::test_add_inventory_item -v

# Coverage report
pytest tests/ --cov=src
```

### Development

```bash
# Install dependencies
pip install -r requirements.txt

# Verify architecture
python -c "from src.db import SQLiteAdapter; from src.services import *; print('✓ All imports working')"

# Run with custom database
python bizhub.py --db mydb.db
```

## Future Roadmap

### Phase 1: Modern UI/UX (Current)
- ✅ Refactored modular architecture
- ✅ 24 passing tests
- 🔄 Desktop UI redesign with modern Tkinter themes
- Product enhancements: Dashboard analytics, Customer loyalty

### Phase 2: Cloud Ready
- Create PostgreSQL adapter (`src/db/postgres_adapter.py`)
- Environment-based config switching
- Multi-tenant support
- Cloud storage for attachments

### Phase 3: Web Interface
- REST API layer (`api/app.py` with FastAPI, deployed on Render)
- Web UI (`bzhub_web/` with Next.js, deployed on Vercel)
- Mobile-responsive design
- Real-time notifications

### Phase 4: Extensions
- Marketplace for plugins
- Custom report builder
- Advanced forecasting
- Multi-location support

## Adding New Features

### Example: Add a new service

```python
# 1. Add to core logic (if needed)
# src/core/__init__.py
class NewCalculator:
    @staticmethod
    def calculate_something(items):
        return sum(i.value for i in items)

# 2. Create service
# src/services/new_service.py
class NewService:
    def __init__(self, db_adapter):
        self.db = db_adapter
    
    def do_something(self):
        from src.core import NewCalculator
        return NewCalculator.calculate_something(...)

# 3. Add to services/__init__.py
from src.services.new_service import NewService

# 4. Use in UI
# src/ui/desktop/bizhub_desktop.py
self.new_service = NewService(self.db)
results = self.new_service.do_something()

# 5. Test it
# tests/test_bizhub_refactored.py
def test_new_service(db):
    service = NewService(db)
    assert service.do_something() == expected
```

## Switching to Cloud Database (Future)

```python
# config.py - Read from environment
DB_TYPE = os.getenv('DB_TYPE', 'sqlite')  # Set to 'postgresql' in cloud

# bizhub.py - Loads appropriate adapter
if DB_TYPE == 'sqlite':
    from src.db import SQLiteAdapter
    db = SQLiteAdapter(DB_FILE)
elif DB_TYPE == 'postgresql':
    from src.db import PostgreSQLAdapter  # Future implementation
    db = PostgreSQLAdapter(DB_URL)

# Services work the same regardless of DB!
auth = AuthService(db)
inventory = InventoryService(db)
```

## Testing Strategy

- **Unit tests** (`src/core/` functions): Fast, no mocks needed
- **Integration tests** (`services` + DB): Use in-memory SQLite
- **UI tests** (future): Selenium for web interface
- **Performance tests** (future): Benchmarks for cloud deployment

## File Structure Quick Reference

| File | Purpose | Dependencies |
|------|---------|---|
| `src/core/__init__.py` | Business logic | None |
| `src/db/base.py` | DB interface | None |
| `src/db/sqlite_adapter.py` | SQLite impl. | sqlite3 |
| `src/services/*.py` | Operations | core + db |
| `src/ui/desktop/bizhub_desktop.py` | Tkinter UI | services |
| `bizhub.py` | Launcher | config + ui |
| `tests/test_bizhub_refactored.py` | Tests | pytest + src |

## Notes for Future Development

1. **Database Switching**: Only the `src/db/` layer needs to change
2. **UI Swapping**: Web UI now lives in `bzhub_web/` (Next.js, Vercel)
3. **API Creation**: Expose services as REST endpoints in `api/app.py`
4. **Offline-First Desktop**: Current design supports offline mode
5. **Cloud Sync**: Services layer handles sync logic independently

## Support & Documentation

- **Business Logic**: See `src/core/__init__.py` for calculators
- **Database Operations**: See `src/db/base.py` for interface
- **API Reference**: See `src/services/` for service methods
- **UI Usage**: See `src/ui/desktop/bizhub_desktop.py` for examples

---

**Last Updated:** February 18, 2026  
**Architecture Version:** 1.1.0 (Web & Cloud Ready)
