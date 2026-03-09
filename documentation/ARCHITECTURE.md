# BizHub - Cloud-Ready ERP Suite Architecture

**Version:** 2.0.0
**Status:** 3-tier architecture — Desktop (Tkinter) + API (FastAPI) + Web (Next.js)

## Overview

BizHub is a complete ERP solution for small businesses with a **3-tier architecture**:

- ✅ **Desktop deployment** (Tkinter — works offline, connects directly to SQLite)
- ✅ **REST API** (FastAPI — exposes all data via HTTP, same SQLite adapter)
- ✅ **Web frontend** (Next.js + Tailwind — connects to API, browser-accessible)
- 🔮 **Cloud database** (PostgreSQL/MySQL — future, swap adapter only)

## 3-Tier Architecture

```
┌─────────────────────┐     ┌──────────────────────┐     ┌──────────────────────┐
│   Desktop (Tkinter) │     │   API (FastAPI)       │     │   Web (Next.js)      │
│   bizhub.py         │     │   bizhub.py --api     │     │   bzhub_web/bzhub_web│
│                     │     │                      │     │                      │
│  src/ui/desktop/    │     │  src/api/main.py     │◄────│  src/app/            │
│  bizhub_desktop.py  │     │  src/api/routers/    │     │  src/lib/api.ts      │
│                     │     │  auth, inventory,    │     │  page.tsx, dashboard,│
│  tabs/              │     │  sales, contacts,    │     │  operations, crm     │
│  - dashboard_tab    │     │  leads, dashboard    │     │                      │
│  - crm_tab          │     │                      │     │  Tailwind CSS        │
│  - crm_leads_tab    │     │  src/api/deps.py     │     │  Primary: #6D28D9   │
│  - inventory_tab    │     │  (shared services)   │     │                      │
│  - pos_tab, hr_tab  │     │                      │     │                      │
└──────────┬──────────┘     └──────────┬───────────┘     └──────────────────────┘
           │                           │
           │         direct            │         via same
           └──────────┬────────────────┘         adapter
                      │
           ┌──────────▼───────────────┐
           │   src/db/sqlite_adapter  │
           │   SQLiteAdapter          │
           │   - inventory.db         │
           │   - CRM tables           │
           │   - HR, Payroll, etc.    │
           └──────────────────────────┘
```

## File Structure

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
│   │   ├── crm_service.py      # CRM — contacts, leads, pipeline, activities
│   │   ├── payroll_service.py
│   │   ├── appraisal_service.py
│   │   └── __init__.py
│   │
│   ├── api/                     # FastAPI REST backend (--api mode)
│   │   ├── main.py             # FastAPI app + CORS + router registration
│   │   ├── deps.py             # Shared DB adapter + service instances
│   │   ├── routers/
│   │   │   ├── auth.py         # POST /auth/login
│   │   │   ├── inventory.py    # GET/POST/PUT/DELETE /inventory
│   │   │   ├── sales.py        # GET /sales, POST /sales/checkout
│   │   │   ├── contacts.py     # GET/POST/PUT/DELETE /contacts
│   │   │   ├── leads.py        # GET/POST/PUT/DELETE /leads, GET /leads/pipeline
│   │   │   └── dashboard.py    # GET /dashboard/kpis, GET /dashboard/trend
│   │   └── __init__.py
│   │
│   ├── ui/
│   │   ├── desktop/
│   │   │   ├── bizhub_desktop.py    # Tkinter desktop app shell
│   │   │   └── tabs/
│   │   │       ├── base_tab.py
│   │   │       ├── dashboard_tab.py
│   │   │       ├── crm_tab.py       # Operations container (CRM first)
│   │   │       ├── crm_leads_tab.py # CRM Leads + Pipeline Kanban
│   │   │       ├── inventory_tab.py
│   │   │       ├── pos_tab.py
│   │   │       ├── hr_tab.py
│   │   │       ├── visitors_tab.py
│   │   │       ├── bills_tab.py
│   │   │       ├── reports_tab.py
│   │   │       └── settings_tab.py
│   │   └── __init__.py
│   │
│   ├── config.py               # Environment-based configuration
│   └── __init__.py
│
├── bzhub_web/bzhub_web/        # Next.js Web Frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx      # Root layout
│   │   │   ├── globals.css     # Tailwind base
│   │   │   ├── page.tsx        # Login page
│   │   │   ├── dashboard/page.tsx   # KPI dashboard
│   │   │   ├── operations/page.tsx  # Operations hub
│   │   │   └── crm/page.tsx         # CRM Kanban (standalone)
│   │   ├── lib/
│   │   │   └── api.ts          # apiFetch + typed API helpers
│   │   └── components/
│   │       └── TopNav.tsx      # Navigation bar
│   ├── package.json
│   ├── tsconfig.json
│   └── tailwind.config.ts
│
├── tests/
│   ├── test_bizhub_refactored.py
│   └── conftest.py
│
├── bizhub.py                   # Main launcher (desktop / --api / --web)
├── .env.example                # Environment variable template
└── requirements.txt
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

Credentials: `admin` / `admin123`

### API Server (FastAPI)

```bash
# Install dependencies first
pip install fastapi 'uvicorn[standard]'

# Start API
python bizhub.py --api
# API docs: http://localhost:8000/docs
# Health: http://localhost:8000/health
```

### Web Frontend (Next.js)

```bash
# Copy environment file
cp bzhub_web/bzhub_web/.env.local.example bzhub_web/bzhub_web/.env.local

# Start dev server (requires Node.js 18+)
cd bzhub_web/bzhub_web
npm run dev
# Visit: http://localhost:3000
```

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
- REST API layer (`api/app.py` with FastAPI)
- Web UI (`src/ui/web/` with Flask + Vue.js)
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
2. **UI Swapping**: Create new adapter in `src/ui/web/` for Flask/Vue
3. **API Creation**: Expose services as REST endpoints in `api/app.py`
4. **Offline-First Desktop**: Current design supports offline mode
5. **Cloud Sync**: Services layer handles sync logic independently

## Support & Documentation

- **Business Logic**: See `src/core/__init__.py` for calculators
- **Database Operations**: See `src/db/base.py` for interface
- **API Reference**: See `src/services/` for service methods
- **UI Usage**: See `src/ui/desktop/bizhub_desktop.py` for examples

---

**Last Updated:** 2026-03-09
**Architecture Version:** 2.0.0 (3-Tier: Desktop + API + Web)
