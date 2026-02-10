# BizHub Quick Start Guide

## Installation

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the application
python bizhub.py
```

## Login Credentials

- **Username:** `admin`
- **Password:** `admin123`

## Running Tests

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/test_bizhub_refactored.py -v

# Run specific test
pytest tests/test_bizhub_refactored.py::test_add_inventory_item
```

## Understanding the Architecture

The code is organized into logical layers:

1. **`src/core/`** - Pure business logic (calculators, validators)
2. **`src/db/`** - Database abstraction (swap SQLite for PostgreSQL later)
3. **`src/services/`** - Business operations (use core + db together)
4. **`src/ui/desktop/`** - Tkinter desktop interface
5. **`src/config.py`** - Configuration management

See `ARCHITECTURE.md` for detailed documentation.

## Common Tasks

### Add a New Inventory Item (Programmatically)

```python
from src.db import SQLiteAdapter
from src.services import InventoryService

db = SQLiteAdapter('inventory.db')
inventory = InventoryService(db)

inventory.add_item('Widget A', quantity=100, threshold=20, 
                   cost_price=10.50, sale_price=25.00, 
                   description='Premium widget')
```

### Get Low Stock Items

```python
from src.db import SQLiteAdapter
from src.services import InventoryService

db = SQLiteAdapter('inventory.db')
inventory = InventoryService(db)

low_stock = inventory.get_low_stock_items()
for item in low_stock:
    print(f"{item[0]} - Stock: {item[1]}, Threshold: {item[2]}")
```

### Calculate POS Total with Discount & Tax

```python
from src.services import POSService

items = [
    {'quantity': 2, 'sale_price': 50.00},
    {'quantity': 1, 'sale_price': 100.00}
]

total = POSService.calculate_total(items)  # 200.00
discounted = POSService.apply_discount(total, 10)  # 180.00
with_tax = POSService.apply_tax(discounted, 18)  # 212.40
print(f"Final amount: ₹{with_tax:.2f}")
```

### Add Employee and Calculate ID Expiry

```python
from src.db import SQLiteAdapter
from src.services import HRService

db = SQLiteAdapter('inventory.db')
hr = HRService(db)

hr.add_employee(
    emp_number='EMP001',
    name='John Doe',
    joining_date='2023-01-15',
    designation='Manager',
    email='john@example.com'
)

expiry = hr.get_employee_id_card_expiry('2023-01-15')
print(f"ID expires on: {expiry}")
```

### Search Inventory

```python
from src.db import SQLiteAdapter
from src.services import InventoryService

db = SQLiteAdapter('inventory.db')
inventory = InventoryService(db)

results = inventory.search('widget')
for item in results:
    print(f"{item[0]}: Qty={item[1]}, Price=₹{item[4]:.2f}")
```

## Database Operations

### SQLite (Current)

```python
from src.db import SQLiteAdapter

db = SQLiteAdapter('my_database.db')
```

### PostgreSQL (Future)

```python
from src.db import PostgreSQLAdapter

db = PostgreSQLAdapter('postgresql://user:pass@localhost/bizhub')
```

The code works the same with both!

## Configuration

Create a `.env` file to customize settings:

```env
DB_TYPE=sqlite
DB_FILE=inventory.db
DEBUG=false
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

Or set environment variables:

```bash
export DB_TYPE=sqlite
export DEBUG=true
python bizhub.py
```

## Troubleshooting

### Module not found errors

```bash
# Make sure you're in the project directory
cd /path/to/C_Love_Coding

# Verify imports work
python -c "from src.db import SQLiteAdapter; print('OK')"
```

### Tests failing

```bash
# Ensure pytest and all dependencies are installed
pip install -r requirements.txt

# Run tests with verbose output
pytest tests/ -vv
```

### Database locked

```bash
# This shouldn't happen with SQLite in desktop mode
# If it does, check for other processes using the DB
lsof inventory.db  # macOS/Linux
```

## Project Structure

```
C_Love_Coding/
├── src/
│   ├── core/                    # Business logic
│   ├── db/                      # Database layer
│   ├── services/                # Services
│   ├── ui/desktop/              # Desktop UI
│   └── config.py
├── tests/                       # Test files
├── bizhub.py                    # Main launcher
├── requirements.txt             # Dependencies
└── README.md                    # This file
```

## Next Steps

1. **Explore the code** - Start with `src/core/__init__.py` to understand business logic
2. **Run tests** - See `pytest tests/` for examples of all features
3. **Modify the UI** - Edit `src/ui/desktop/bizhub_desktop.py` to customize
4. **Add features** - Create new services in `src/services/`

## Documentation Links

- **Architecture Details:** See `ARCHITECTURE.md`
- **Refactoring Summary:** See `REFACTORING_SUMMARY.md`
- **Code Comments:** Each file has inline documentation
- **API Reference:** Check docstrings in service classes

## Support

- Review test files for usage examples
- Check ARCHITECTURE.md for design decisions
- Look at existing services for patterns

---

**Happy coding with BizHub! 🚀**
