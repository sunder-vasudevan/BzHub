import pytest
from unittest.mock import patch, MagicMock
from api.payroll import (
    generate_payslip,
    get_employee_payslips,
    get_payslip_details,
    generate_payslip_pdf,
    generate_bulk_payslips
)

# Test payslip generation
def test_generate_payslip():
    """Test payslip creation and storage."""
    from api.payroll import PayrollCalculation
    
    calc = PayrollCalculation(
        employee_id="EMP_001",
        base_salary=50000,
        allowances={"dearness": 5000, "house_rent": 10000},
        deductions_config={
            "tax_rate": 0.10,
            "insurance": 500,
            "loan_emi": 0,
            "professional_tax": 200
        }
    )
    
    # Mock supabase insert
    with patch('api.payroll.supabase') as mock_db:
        mock_response = MagicMock()
        mock_response.data = [{"id": "PAYSLIP_001"}]
        mock_db.table().insert().execute.return_value = mock_response
        
        result = generate_payslip(calc)
        
        assert result["success"] == True
        assert result["id"] == "PAYSLIP_001"
        assert result["payslip"]["employee_id"] == "EMP_001"

def test_get_employee_payslips():
    """Test retrieving all payslips for an employee."""
    with patch('api.payroll.supabase') as mock_db:
        mock_response = MagicMock()
        mock_response.data = [
            {"id": "PAYSLIP_001", "period": "April 2026"},
            {"id": "PAYSLIP_002", "period": "March 2026"}
        ]
        mock_db.table().select().eq().execute.return_value = mock_response
        
        result = get_employee_payslips("EMP_001")
        
        assert result["employee_id"] == "EMP_001"
        assert len(result["payslips"]) == 2

def test_get_payslip_details():
    """Test retrieving specific payslip."""
    with patch('api.payroll.supabase') as mock_db:
        mock_response = MagicMock()
        mock_response.data = [
            {
                "id": "PAYSLIP_001",
                "employee_id": "EMP_001",
                "period": "April 2026",
                "gross_salary": 65000,
                "net_salary": 57800
            }
        ]
        mock_db.table().select().eq().eq.return_value.execute.return_value = mock_response
        
        result = get_payslip_details("EMP_001", "PAYSLIP_001")
        
        assert result["id"] == "PAYSLIP_001"
        assert result["net_salary"] == 57800

def test_generate_payslip_pdf():
    """Test PDF generation."""
    with patch('api.payroll.supabase') as mock_db:
        mock_response = MagicMock()
        mock_response.data = [
            {
                "id": "PAYSLIP_001",
                "employee_id": "EMP_001",
                "period": "April 2026",
                "gross_salary": 65000,
                "deductions": {"tax": 6500, "insurance": 500, "professional_tax": 200},
                "net_salary": 57800
            }
        ]
        mock_db.table().select().eq().execute.return_value = mock_response
        
        result = generate_payslip_pdf("PAYSLIP_001")
        
        assert result["success"] == True
        assert "pdf_base64" in result
        assert result["payslip_id"] == "PAYSLIP_001"

def test_generate_bulk_payslips():
    """Test bulk payslip generation."""
    with patch('api.payroll.supabase') as mock_db:
        mock_response = MagicMock()
        mock_response.data = [{"id": "PAYSLIP_ID"}]
        mock_db.table().insert().execute.return_value = mock_response
        
        employee_ids = ["EMP_001", "EMP_002", "EMP_003"]
        result = generate_bulk_payslips(employee_ids)
        
        assert result["total"] == 3
        assert result["generated"] == 3
        assert len(result["results"]) == 3

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
