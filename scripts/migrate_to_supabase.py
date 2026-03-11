"""
Migrate local SQLite data → Supabase
Run: .venv/bin/python scripts/migrate_to_supabase.py
"""
import sqlite3
import os
import sys

try:
    from supabase import create_client
except ImportError:
    print("Installing supabase...")
    os.system(".venv/bin/pip install supabase -q")
    from supabase import create_client

SUPABASE_URL = "https://jltscsnngvdrivqirjcb.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpsdHNjc25uZ3Zkcml2cWlyamNiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzEzNjc5OTcsImV4cCI6MjA4Njk0Mzk5N30.t-hS2gcw8YXOhASUeqE73yvC7aVqTuX_U3NP6uxX7OU"
DB_PATH = "inventory.db"

sb = create_client(SUPABASE_URL, SUPABASE_KEY)
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

def migrate(table, query, transform):
    cur.execute(query)
    rows = [transform(dict(r)) for r in cur.fetchall()]
    if not rows:
        print(f"  {table}: no rows, skipping")
        return
    # Insert in batches of 100
    for i in range(0, len(rows), 100):
        batch = rows[i:i+100]
        try:
            sb.table(table).upsert(batch).execute()
        except Exception as e:
            print(f"  {table} batch error: {e}")
            continue
    print(f"  {table}: {len(rows)} rows migrated")

print("Starting migration...\n")

# Inventory
migrate("inventory",
    "SELECT item_name, quantity, threshold, cost_price, sale_price, description, image_path FROM inventory",
    lambda r: {k: v for k, v in r.items() if v is not None or k in ("item_name",)}
)

# Sales
migrate("sales",
    "SELECT sale_date, item_name, quantity, sale_price, total_amount, username FROM sales",
    lambda r: {**r, "sale_date": (r.get("sale_date") or "")[:10] or None,
               "username": r.get("username") or "admin"}
)

# CRM Contacts
migrate("crm_contacts",
    "SELECT name, company, email, phone, source, status, notes, created_at FROM crm_contacts",
    lambda r: {k: (v or "") if k != "created_at" else v for k, v in r.items()}
)

# CRM Leads (without contact_id FK to avoid constraint issues)
migrate("crm_leads",
    "SELECT title, stage, value, probability, owner, notes, created_at, updated_at FROM crm_leads",
    lambda r: {k: (v if v is not None else ("" if isinstance(v, str) else 0)) for k, v in r.items()}
)

# Employees
migrate("employees",
    """SELECT emp_number, name, joining_date, designation, manager, team,
              email, phone, emergency_contact, is_active FROM employees WHERE is_active=1""",
    lambda r: {**r, "is_active": bool(r.get("is_active", 1))}
)

# Company info
cur.execute("SELECT * FROM company_info LIMIT 1")
row = cur.fetchone()
if row:
    data = dict(row)
    data["id"] = 1
    try:
        sb.table("company_info").upsert([data]).execute()
        print("  company_info: migrated")
    except Exception as e:
        print(f"  company_info error: {e}")

conn.close()
print("\nDone!")
