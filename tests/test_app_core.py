import os
import sqlite3
import tkinter as tk

import pytest

from inventory_crm_sqlite import InventoryCRMApp


@pytest.fixture()
def app(tmp_path):
    db_path = tmp_path / "test_inventory.db"
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tkinter display not available")
    root.withdraw()
    try:
        app_instance = InventoryCRMApp(root, db_file=str(db_path))
        yield app_instance
    finally:
        root.destroy()


def test_admin_user_created_and_authenticates(app):
    assert app.authenticate_user("admin", "admin123") is True
    assert app.authenticate_user("admin", "wrongpass") is False


def test_hash_password_deterministic(app):
    p1 = app.hash_password("secret")
    p2 = app.hash_password("secret")
    p3 = app.hash_password("secret2")
    assert p1 == p2
    assert p1 != p3


def test_employee_table_has_expected_columns(app):
    conn = sqlite3.connect(app.db_file)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(employees)")
    cols = {row[1] for row in cursor.fetchall()}
    conn.close()

    for col in {"emp_number", "emergency_contact", "photo_path"}:
        assert col in cols


def test_fetch_inventory_and_low_stock(app):
    conn = sqlite3.connect(app.db_file)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO inventory (item_name, quantity, threshold, cost_price, sale_price, description) VALUES (?, ?, ?, ?, ?, ?)",
        ("Widget A", 2, 5, 1.25, 2.50, "Test A"),
    )
    cursor.execute(
        "INSERT INTO inventory (item_name, quantity, threshold, cost_price, sale_price, description) VALUES (?, ?, ?, ?, ?, ?)",
        ("Widget B", 10, 5, 2.00, 4.00, "Test B"),
    )
    conn.commit()
    conn.close()

    rows = app.fetch_inventory()
    names = [r[0] for r in rows]
    assert "Widget A" in names
    assert "Widget B" in names

    low_stock = app.get_low_stock_items()
    assert ("Widget A", 2, 5) in low_stock
    assert ("Widget B", 10, 5) not in low_stock


def test_fetch_inventory_search(app):
    conn = sqlite3.connect(app.db_file)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO inventory (item_name, quantity, threshold, cost_price, sale_price, description) VALUES (?, ?, ?, ?, ?, ?)",
        ("Blue Pen", 3, 2, 0.50, 1.00, "Stationery"),
    )
    cursor.execute(
        "INSERT INTO inventory (item_name, quantity, threshold, cost_price, sale_price, description) VALUES (?, ?, ?, ?, ?, ?)",
        ("Red Pen", 5, 2, 0.50, 1.00, "Stationery"),
    )
    conn.commit()
    conn.close()

    rows = app.fetch_inventory(search_query="Blue")
    assert len(rows) == 1
    assert rows[0][0] == "Blue Pen"


def test_fetch_visitors(app):
    conn = sqlite3.connect(app.db_file)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO visitors (name, phone, email, company) VALUES (?, ?, ?, ?)",
        ("Alice", "123", "alice@example.com", "Acme"),
    )
    cursor.execute(
        "INSERT INTO visitors (name, phone, email, company) VALUES (?, ?, ?, ?)",
        ("Bob", "456", "bob@example.com", "Beta"),
    )
    conn.commit()
    conn.close()

    rows = app.fetch_visitors(search_query="alice")
    assert len(rows) == 1
    assert rows[0][0] == "Alice"


def test_export_rows_to_excel_creates_file(app, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    headers = ["ColA", "ColB"]
    rows = [("A1", "B1"), ("A2", "B2")]
    out_path = app.export_rows_to_excel(headers, rows, default_name_prefix="test_export")
    assert os.path.exists(out_path)


def test_send_email_raises_if_missing_config(app):
    with pytest.raises(RuntimeError):
        app.send_email("Test", "Body")
