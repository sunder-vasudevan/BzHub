"""Updated tests for BizHub refactored architecture."""
import pytest
import tkinter as tk
from src.db import SQLiteAdapter
from src.services import (
    AuthService, InventoryService, POSService, HRService,
    VisitorService, EmailService, ActivityService, CompanyService
)


@pytest.fixture()
def db(tmp_path):
    """Create temporary database for testing."""
    db_path = tmp_path / "test_bizhub.db"
    return SQLiteAdapter(str(db_path))


@pytest.fixture()
def services(db):
    """Create service instances."""
    return {
        'auth': AuthService(db),
        'inventory': InventoryService(db),
        'pos': POSService(db),
        'hr': HRService(db),
        'visitor': VisitorService(db),
        'email': EmailService(db),
        'activity': ActivityService(db),
        'company': CompanyService(db),
    }


# === AUTH SERVICE TESTS ===

def test_admin_user_created(db):
    """Test default admin user is created."""
    auth = AuthService(db)
    assert auth.authenticate('admin', 'admin123') is True


def test_admin_authentication_fails_with_wrong_password(db):
    """Test authentication fails with wrong password."""
    auth = AuthService(db)
    assert auth.authenticate('admin', 'wrongpass') is False


def test_get_user_role(db):
    """Test get user role."""
    auth = AuthService(db)
    role = auth.get_user_role('admin')
    assert role == 'admin'


def test_is_admin(db):
    """Test is_admin check."""
    auth = AuthService(db)
    assert auth.is_admin('admin') is True


# === INVENTORY SERVICE TESTS ===

def test_add_inventory_item(db):
    """Test adding inventory item."""
    inv = InventoryService(db)
    result = inv.add_item('Widget A', 10, 5, 1.50, 3.00, 'Test widget')
    assert result is True
    items = inv.get_all_items()
    assert len(items) == 1
    assert items[0][0] == 'Widget A'


def test_get_inventory_value(db):
    """Test inventory value calculation."""
    inv = InventoryService(db)
    inv.add_item('Item1', 10, 5, 2.0, 4.0)
    inv.add_item('Item2', 5, 2, 3.0, 6.0)
    value = inv.get_inventory_value()
    expected = (10 * 2.0) + (5 * 3.0)
    assert value == expected


def test_low_stock_items(db):
    """Test low stock detection."""
    inv = InventoryService(db)
    inv.add_item('Low Stock Item', 2, 5, 1.0, 2.0)
    inv.add_item('Adequate Stock', 10, 5, 1.0, 2.0)
    low_stock = inv.get_low_stock_items()
    assert len(low_stock) == 1
    assert low_stock[0][0] == 'Low Stock Item'


def test_search_inventory(db):
    """Test inventory search."""
    inv = InventoryService(db)
    inv.add_item('Blue Pen', 5, 2, 0.50, 1.00)
    inv.add_item('Red Pen', 5, 2, 0.50, 1.00)
    results = inv.search('Blue')
    assert len(results) == 1
    assert results[0][0] == 'Blue Pen'


def test_update_inventory_item(db):
    """Test updating inventory item."""
    inv = InventoryService(db)
    inv.add_item('Item', 5, 2, 1.0, 2.0)
    inv.update_item('Item', quantity=10, sale_price=3.0)
    item = inv.get_item('Item')
    assert item['quantity'] == 10
    assert item['sale_price'] == 3.0


def test_delete_inventory_item(db):
    """Test deleting inventory item."""
    inv = InventoryService(db)
    inv.add_item('Item', 5, 2, 1.0, 2.0)
    assert len(inv.get_all_items()) == 1
    inv.delete_item('Item')
    assert len(inv.get_all_items()) == 0


# === POS SERVICE TESTS ===

def test_pos_calculate_total():
    """Test POS total calculation."""
    items = [
        {'quantity': 2, 'sale_price': 10.0},
        {'quantity': 3, 'sale_price': 5.0}
    ]
    total = POSService.calculate_total(items)
    expected = (2 * 10.0) + (3 * 5.0)
    assert total == expected


def test_pos_apply_discount():
    """Test POS discount."""
    total = POSService.apply_discount(100.0, 10.0)
    assert total == 90.0


def test_pos_apply_tax():
    """Test POS tax."""
    total = POSService.apply_tax(100.0, 18.0)
    assert total == 118.0


def test_record_sale(db):
    """Test recording a sale."""
    pos = POSService(db)
    result = pos.record_sale('Widget', 5, 2.0, 'admin')
    assert result is True


def test_today_sales_total(db):
    """Test today's sales total."""
    pos = POSService(db)
    pos.record_sale('Item1', 2, 5.0, 'admin')
    pos.record_sale('Item2', 3, 4.0, 'admin')
    total = pos.get_today_sales_total()
    expected = (2 * 5.0) + (3 * 4.0)
    assert total == expected


# === HR SERVICE TESTS ===

def test_add_employee(db):
    """Test adding employee."""
    hr = HRService(db)
    result = hr.add_employee('EMP001', 'John Doe', '2023-01-15', 'Manager', 'CEO', 'Sales', 'john@test.com', '9876543210', 'Emergency Contact', '', 'Notes')
    assert result is True
    employees = hr.get_all_employees()
    assert len(employees) == 1


def test_get_employee_id_card_expiry(db):
    """Test ID card expiry calculation."""
    hr = HRService(db)
    expiry = hr.get_employee_id_card_expiry('2023-01-15')
    expected_expiry = '2024-01-15'
    assert expiry == expected_expiry


def test_add_employee_appraisal(db):
    """Test adding employee appraisal."""
    hr = HRService(db)
    hr.add_employee('EMP001', 'John', '2023-01-15', 'Manager')
    employees = hr.get_all_employees()
    emp_id = employees[0][0]
    result = hr.add_appraisal(emp_id, '2023-12-31', 'Excellent', 'Great performance')
    assert result is True


def test_add_employee_goal(db):
    """Test adding employee goal."""
    hr = HRService(db)
    hr.add_employee('EMP001', 'John', '2023-01-15', 'Manager')
    employees = hr.get_all_employees()
    emp_id = employees[0][0]
    result = hr.add_goal(emp_id, 'Complete project X', 'In Progress', '2024-06-30', 'Important goal')
    assert result is True


# === VISITOR SERVICE TESTS ===

def test_add_visitor(db):
    """Test adding visitor."""
    visitor = VisitorService(db)
    result = visitor.add_visitor('Alice', 'NYC', '9876543210', 'alice@test.com', 'Acme Corp', 'Good customer')
    assert result is True
    visitors = visitor.get_all_visitors()
    assert len(visitors) == 1


def test_search_visitors(db):
    """Test searching visitors."""
    visitor = VisitorService(db)
    visitor.add_visitor('Alice', phone='9876543210', email='alice@test.com')
    visitor.add_visitor('Bob', phone='9876543211', email='bob@test.com')
    results = visitor.search('alice')
    assert len(results) == 1


def test_visitor_count(db):
    """Test visitor count."""
    visitor = VisitorService(db)
    visitor.add_visitor('Alice')
    visitor.add_visitor('Bob')
    assert visitor.get_total_visitors_count() == 2


# === COMPANY SERVICE TESTS ===

def test_save_and_get_company_info(db):
    """Test saving and retrieving company info."""
    company = CompanyService(db)
    company.save_info('Acme Corp', '123 Main St', '555-1234', 'info@acme.com', 'TAX123', 'Bank: XYZ')
    info = company.get_info()
    assert info is not None
    assert info['company_name'] == 'Acme Corp'
    assert info['tax_id'] == 'TAX123'


# === ACTIVITY SERVICE TESTS ===

def test_log_activity(db):
    """Test logging activity."""
    activity = ActivityService(db)
    activity.log('admin', 'Test Action', 'This is a test')
    logs = activity.get_activity_log('admin')
    assert len(logs) > 0
