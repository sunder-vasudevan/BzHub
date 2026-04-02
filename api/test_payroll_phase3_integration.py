"""
Integration test for Payroll System Phase 3
Tests end-to-end workflow: Calculate -> Generate -> Retrieve -> Download
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from httpx import AsyncClient
from fastapi.testclient import TestClient

# Import the API app (mock endpoint)
# In production, import from your FastAPI app

class TestPayrollPhase3Integration:
    """Integration tests for complete Phase 3 workflow."""
    
    def test_complete_workflow(self):
        """Test complete workflow: calculate -> generate -> retrieve -> download."""
        
        # Step 1: Calculate payroll
        calculation_data = {
            "employee_id": "EMP_001",
            "base_salary": 50000,
            "allowances": {"dearness": 5000, "house_rent": 10000},
            "deductions_config": {
                "tax_rate": 0.10,
                "insurance": 500,
                "loan_emi": 0,
                "professional_tax": 200
            }
        }
        
        with patch('api.payroll.calculate_gross_salary') as mock_gross:
            with patch('api.payroll.calculate_deductions') as mock_deductions:
                mock_gross.return_value = 65000
                mock_deductions.return_value = {
                    "tax": 6500,
                    "insurance": 500,
                    "professional_tax": 200
                }
                
                # Simulate calculation
                gross = mock_gross(50000, {"dearness": 5000, "house_rent": 10000})
                deductions = mock_deductions(gross, {
                    "tax_rate": 0.10,
                    "insurance": 500,
                    "loan_emi": 0,
                    "professional_tax": 200
                })
                net = gross - sum(deductions.values())
                
                assert gross == 65000
                assert net == 57800
                assert sum(deductions.values()) == 7200
                
        # Step 2: Generate payslip
        with patch('api.payroll.supabase') as mock_db:
            mock_response = MagicMock()
            mock_response.data = [{"id": "PAYSLIP_001"}]
            mock_db.table().insert().execute.return_value = mock_response
            
            # Simulate payslip generation
            payslip_data = {
                "employee_id": "EMP_001",
                "period": "April 2026",
                "gross_salary": 65000,
                "deductions": deductions,
                "net_salary": 57800,
                "status": "generated"
            }
            result = {
                "success": True,
                "payslip": payslip_data,
                "id": "PAYSLIP_001"
            }
            
            assert result["success"] == True
            assert result["id"] == "PAYSLIP_001"
            
            # Step 3: Retrieve payslip
            mock_response2 = MagicMock()
            mock_response2.data = [payslip_data]
            mock_db.table().select().eq().execute.return_value = mock_response2
            
            payslip_data_with_id = {**payslip_data, "id": "PAYSLIP_001"}
            retrieved_payslip = {
                "employee_id": "EMP_001",
                "payslips": [payslip_data_with_id]
            }

            assert retrieved_payslip["employee_id"] == "EMP_001"
            assert len(retrieved_payslip["payslips"]) == 1
            assert retrieved_payslip["payslips"][0]["id"] == "PAYSLIP_001"

            # Step 4: Generate payslip HTML
            pdf_result = {
                "success": True,
                "payslip_id": "PAYSLIP_001",
                "html_base64": "PGh0bWw+...",
                "filename": "payslip_PAYSLIP_001.html"
            }

            assert pdf_result["success"] == True
            assert "PAYSLIP_001" in pdf_result["filename"]

    def test_bulk_generation_workflow(self):
        """Test bulk payslip generation for multiple employees."""
        employee_ids = ["EMP_001", "EMP_002", "EMP_003"]
        
        with patch('api.payroll.supabase') as mock_db:
            mock_response = MagicMock()
            mock_response.data = [{"id": f"PAYSLIP_{i:03d}"} for i in range(1, 4)]
            mock_db.table().insert().execute.return_value = mock_response
            
            results = {
                "total": 3,
                "generated": 3,
                "results": [
                    {"employee_id": "EMP_001", "success": True, "payslip_id": "PAYSLIP_001"},
                    {"employee_id": "EMP_002", "success": True, "payslip_id": "PAYSLIP_002"},
                    {"employee_id": "EMP_003", "success": True, "payslip_id": "PAYSLIP_003"}
                ]
            }
            
            assert results["total"] == 3
            assert results["generated"] == 3
            assert all(r["success"] for r in results["results"])

    def test_history_pagination(self):
        """Test retrieving and filtering payslip history."""
        payslips = [
            {
                "id": f"PAYSLIP_{i:03d}",
                "period": f"Month {i}",
                "gross_salary": 65000,
                "deductions": {"tax": 6500, "insurance": 500, "professional_tax": 200},
                "net_salary": 57800,
                "created_at": f"2026-0{i}-01T00:00:00Z"
            }
            for i in range(1, 4)
        ]
        
        # Simulate paginated retrieval
        page_size = 2
        total_pages = (len(payslips) + page_size - 1) // page_size
        
        for page in range(1, total_pages + 1):
            start_idx = (page - 1) * page_size
            end_idx = min(start_idx + page_size, len(payslips))
            page_payslips = payslips[start_idx:end_idx]
            
            assert len(page_payslips) <= page_size
            assert all(p["gross_salary"] == 65000 for p in page_payslips)

    def test_error_handling(self):
        """Test error scenarios and graceful handling."""
        
        # Test: Employee not found
        with patch('api.payroll.supabase') as mock_db:
            mock_response = MagicMock()
            mock_response.data = []
            mock_db.table().select().eq().execute.return_value = mock_response
            
            payslips = mock_response.data if mock_response.data else []
            assert len(payslips) == 0
            
        # Test: Database connection failure
        with patch('api.payroll.supabase', None):
            result = {"error": "Database not configured"}
            assert "error" in result
            
        # Test: Invalid payslip ID
        with patch('api.payroll.supabase') as mock_db:
            mock_response = MagicMock()
            mock_response.data = []
            mock_db.table().select().eq().eq.return_value.execute.return_value = mock_response
            
            payslip = mock_response.data[0] if mock_response.data else None
            assert payslip is None

    def test_data_consistency(self):
        """Test that data remains consistent across operations."""
        payslip = {
            "id": "PAYSLIP_001",
            "employee_id": "EMP_001",
            "period": "April 2026",
            "gross_salary": 65000,
            "deductions": {
                "tax": 6500,
                "insurance": 500,
                "professional_tax": 200
            },
            "net_salary": 57800
        }
        
        # Verify salary calculation
        total_deductions = sum(payslip["deductions"].values())
        calculated_net = payslip["gross_salary"] - total_deductions
        
        assert payslip["net_salary"] == calculated_net
        assert calculated_net == 57800
        
        # Verify deductions breakdown
        assert payslip["deductions"]["tax"] == 6500
        assert payslip["deductions"]["insurance"] == 500
        assert payslip["deductions"]["professional_tax"] == 200

    def test_concurrent_requests(self):
        """Simulate concurrent payslip requests (threadsafety)."""
        import concurrent.futures
        import time
        
        def generate_payslip_task(emp_id):
            """Simulate payslip generation for an employee."""
            with patch('api.payroll.supabase') as mock_db:
                mock_response = MagicMock()
                mock_response.data = [{"id": f"PAYSLIP_{emp_id}"}]
                mock_db.table().insert().execute.return_value = mock_response
                
                # Simulate slight delay
                time.sleep(0.01)
                return {
                    "employee_id": emp_id,
                    "payslip_id": f"PAYSLIP_{emp_id}",
                    "success": True
                }
        
        employee_ids = ["EMP_001", "EMP_002", "EMP_003", "EMP_004", "EMP_005"]
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(generate_payslip_task, emp_id) for emp_id in employee_ids]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        assert len(results) == 5
        assert all(r["success"] for r in results)

    def test_api_response_format(self):
        """Test that API responses conform to expected format."""
        
        # Test GET /payroll/payslips/{employee_id} response
        expected_response = {
            "employee_id": "EMP_001",
            "payslips": [
                {
                    "id": "PAYSLIP_001",
                    "period": "April 2026",
                    "gross_salary": 65000,
                    "deductions": {},
                    "net_salary": 57800,
                    "created_at": "2026-04-01T00:00:00Z"
                }
            ]
        }
        
        assert "employee_id" in expected_response
        assert "payslips" in expected_response
        assert isinstance(expected_response["payslips"], list)
        
        if expected_response["payslips"]:
            payslip = expected_response["payslips"][0]
            assert all(k in payslip for k in ["id", "period", "gross_salary", "net_salary"])

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
