import pytest
from unittest.mock import patch, MagicMock

# Mock supabase_client before importing payroll module
with patch('supabase_client.supabase', MagicMock()):
    from payroll import (
        calculate_gross_salary,
        calculate_deductions,
        calculate_net_salary
    )

def test_calculate_gross_salary():
    """Test gross salary calculation."""
    base = 50000
    allowances = {"dearness": 5000, "house_rent": 10000}
    gross = calculate_gross_salary(base, allowances)
    assert gross == 65000

def test_calculate_gross_salary_no_allowances():
    """Test gross with no allowances."""
    base = 50000
    gross = calculate_gross_salary(base, {})
    assert gross == 50000

def test_calculate_deductions():
    """Test deductions calculation."""
    gross = 65000
    config = {
        "tax_rate": 0.10,
        "insurance": 500,
        "loan_emi": 5000,
        "professional_tax": 200
    }
    deductions = calculate_deductions(gross, config)
    
    assert deductions["tax"] == 6500  # 10% of 65000
    assert deductions["insurance"] == 500
    assert deductions["loan_emi"] == 5000
    assert deductions["professional_tax"] == 200

def test_calculate_deductions_partial_config():
    """Test with partial deduction config."""
    gross = 65000
    config = {"tax_rate": 0.10}
    deductions = calculate_deductions(gross, config)
    
    assert deductions["tax"] == 6500
    assert "insurance" not in deductions
    assert "loan_emi" not in deductions

def test_calculate_net_salary():
    """Test net salary calculation."""
    gross = 65000
    deductions = {
        "tax": 6500,
        "insurance": 500,
        "loan_emi": 5000,
        "professional_tax": 200
    }
    net = calculate_net_salary(gross, deductions)
    assert net == 52800  # 65000 - (6500 + 500 + 5000 + 200)

def test_calculate_net_salary_no_deductions():
    """Test net salary with no deductions."""
    gross = 65000
    net = calculate_net_salary(gross, {})
    assert net == 65000

def test_payroll_complete_scenario():
    """Test complete payroll calculation scenario."""
    base_salary = 50000
    allowances = {"dearness": 5000, "house_rent": 10000}
    config = {
        "tax_rate": 0.10,
        "insurance": 500,
        "loan_emi": 5000,
        "professional_tax": 200
    }
    
    gross = calculate_gross_salary(base_salary, allowances)
    assert gross == 65000
    
    deductions = calculate_deductions(gross, config)
    assert sum(deductions.values()) == 12200
    
    net = calculate_net_salary(gross, deductions)
    assert net == 52800
