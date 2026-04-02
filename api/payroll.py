from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
import os

# Initialize supabase only if environment variables are available
try:
    from supabase_client import supabase
except Exception as e:
    # Allow module to load without supabase for testing
    supabase = None

router = APIRouter()

# Pydantic models for request/response
class SalaryConfig(BaseModel):
    base_salary: float
    allowances: dict = {}
    deductions_config: dict = {}

class PayrollCalculation(BaseModel):
    employee_id: str
    base_salary: float
    allowances: dict = {}
    deductions_config: dict = {}

class PayslipResponse(BaseModel):
    employee_id: str
    gross_salary: float
    deductions: dict
    net_salary: float
    period: str

# Core calculation functions
def calculate_gross_salary(base_salary: float, allowances: dict) -> float:
    """Calculate gross salary from base + allowances."""
    return base_salary + sum(allowances.values())

def calculate_deductions(gross_salary: float, deductions_config: dict) -> dict:
    """
    Calculate total deductions based on config.
    Config format: {"tax_rate": 0.10, "insurance": 500, "loan_emi": 2000}
    """
    deductions = {}
    
    # Tax deduction (percentage of gross)
    if "tax_rate" in deductions_config:
        deductions["tax"] = gross_salary * deductions_config["tax_rate"]
    else:
        deductions["tax"] = 0
    
    # Fixed deductions
    if "insurance" in deductions_config:
        deductions["insurance"] = deductions_config["insurance"]
    
    if "loan_emi" in deductions_config:
        deductions["loan_emi"] = deductions_config["loan_emi"]
    
    # Professional tax (fixed in many locales)
    if "professional_tax" in deductions_config:
        deductions["professional_tax"] = deductions_config["professional_tax"]
    
    return deductions

def calculate_net_salary(gross_salary: float, deductions: dict) -> float:
    """Calculate net salary = gross - total deductions."""
    return gross_salary - sum(deductions.values())

# REST API Endpoints

@router.post("/payroll/calculate", tags=["Payroll"])
def calculate_payroll(calc: PayrollCalculation) -> PayslipResponse:
    """
    Calculate payroll for an employee.
    Returns gross, deductions breakdown, and net salary.
    """
    gross = calculate_gross_salary(calc.base_salary, calc.allowances)
    deductions = calculate_deductions(gross, calc.deductions_config)
    net = calculate_net_salary(gross, deductions)
    
    return PayslipResponse(
        employee_id=calc.employee_id,
        gross_salary=gross,
        deductions=deductions,
        net_salary=net,
        period=datetime.now().strftime("%B %Y")
    )

@router.get("/payroll/config", tags=["Payroll"])
def get_payroll_config():
    """Retrieve default payroll deduction configuration."""
    if not supabase:
        return {
            "config": {
                "tax_rate": 0.10,
                "insurance": 500,
                "loan_emi": 0,
                "professional_tax": 200
            }
        }
    try:
        response = supabase.table("payroll_config").select("*").execute()
        config = response.data[0] if response.data else {
            "tax_rate": 0.10,
            "insurance": 500,
            "loan_emi": 0,
            "professional_tax": 200
        }
        return {"config": config}
    except Exception as e:
        return {
            "config": {
                "tax_rate": 0.10,
                "insurance": 500,
                "loan_emi": 0,
                "professional_tax": 200
            },
            "error": str(e)
        }

@router.post("/payroll/payslip", tags=["Payroll"])
def generate_payslip(calc: PayrollCalculation) -> dict:
    """
    Generate and store a payslip record.
    """
    gross = calculate_gross_salary(calc.base_salary, calc.allowances)
    deductions = calculate_deductions(gross, calc.deductions_config)
    net = calculate_net_salary(gross, deductions)
    
    payslip_data = {
        "employee_id": calc.employee_id,
        "gross_salary": gross,
        "deductions": deductions,
        "net_salary": net,
        "period": datetime.now().strftime("%B %Y"),
        "created_at": datetime.now().isoformat(),
        "status": "generated"
    }
    
    if not supabase:
        return {
            "success": True,
            "payslip": payslip_data,
            "id": None,
            "note": "Database not configured - payslip not saved"
        }
    
    try:
        response = supabase.table("payroll_records").insert(payslip_data).execute()
        return {
            "success": True,
            "payslip": payslip_data,
            "id": response.data[0].get("id") if response.data else None
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to generate payslip: {str(e)}")

@router.get("/payroll/payslips/{employee_id}", tags=["Payroll"])
def get_employee_payslips(employee_id: str):
    """Retrieve all payslips for an employee."""
    if not supabase:
        return {"employee_id": employee_id, "payslips": []}
    
    try:
        response = supabase.table("payroll_records").select("*").eq("employee_id", employee_id).execute()
        payslips = response.data if hasattr(response, 'data') else []
        return {"employee_id": employee_id, "payslips": payslips}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to retrieve payslips: {str(e)}")

@router.get("/payroll/payslips/{employee_id}/{payslip_id}", tags=["Payroll"])
def get_payslip_details(employee_id: str, payslip_id: str):
    """Retrieve a specific payslip by ID."""
    if not supabase:
        return {"error": "Database not configured"}
    
    try:
        response = supabase.table("payroll_records").select("*").eq("id", payslip_id).eq("employee_id", employee_id).execute()
        payslip = response.data[0] if response.data else None
        if not payslip:
            raise HTTPException(status_code=404, detail="Payslip not found")
        return payslip
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to retrieve payslip: {str(e)}")

@router.post("/payroll/payslip-pdf/{payslip_id}", tags=["Payroll"])
def generate_payslip_pdf(payslip_id: str):
    """Generate PDF for a payslip (returns base64 encoded PDF)."""
    if not supabase:
        return {"error": "Database not configured"}
    
    try:
        # Retrieve payslip
        response = supabase.table("payroll_records").select("*").eq("id", payslip_id).execute()
        payslip = response.data[0] if response.data else None
        if not payslip:
            raise HTTPException(status_code=404, detail="Payslip not found")
        
        deductions = payslip.get('deductions', {})
        deduction_rows = "".join(
            f"<tr><td>{k.replace('_', ' ').title()}</td><td style='text-align:right'>₹{v:,.2f}</td></tr>"
            for k, v in deductions.items()
        )
        total_deductions = sum(deductions.values())
        html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 40px auto; color: #333; }}
  h1 {{ color: #1d4ed8; border-bottom: 2px solid #1d4ed8; padding-bottom: 8px; }}
  table {{ width: 100%; border-collapse: collapse; margin: 16px 0; }}
  td {{ padding: 8px 4px; border-bottom: 1px solid #e5e7eb; }}
  .total {{ font-weight: bold; border-top: 2px solid #333; }}
  .net {{ font-size: 1.4em; color: #16a34a; font-weight: bold; }}
</style>
</head>
<body>
  <h1>PAYSLIP</h1>
  <table>
    <tr><td><strong>Employee ID</strong></td><td>{payslip.get('employee_id')}</td></tr>
    <tr><td><strong>Period</strong></td><td>{payslip.get('period')}</td></tr>
    <tr><td><strong>Gross Salary</strong></td><td>₹{payslip.get('gross_salary', 0):,.2f}</td></tr>
  </table>
  <h3>Deductions</h3>
  <table>
    {deduction_rows}
    <tr class="total"><td>Total Deductions</td><td style='text-align:right'>₹{total_deductions:,.2f}</td></tr>
  </table>
  <p class="net">Net Salary: ₹{payslip.get('net_salary', 0):,.2f}</p>
  <p style="color:#9ca3af;font-size:0.8em">Generated: {datetime.now().strftime('%d %b %Y, %H:%M')}</p>
</body>
</html>"""

        import base64
        html_b64 = base64.b64encode(html_content.encode()).decode()

        return {
            "success": True,
            "payslip_id": payslip_id,
            "html_base64": html_b64,
            "filename": f"payslip_{payslip_id}.html"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to generate PDF: {str(e)}")

class BulkPayrollEntry(BaseModel):
    employee_id: str
    base_salary: float
    allowances: dict = {}
    deductions_config: dict = {}

@router.post("/payroll/payslip-bulk", tags=["Payroll"])
def generate_bulk_payslips(entries: list[BulkPayrollEntry]):
    """Generate payslips for multiple employees with salary data."""
    if not supabase:
        return {"error": "Database not configured", "count": 0}

    results = []
    for entry in entries:
        try:
            gross = calculate_gross_salary(entry.base_salary, entry.allowances)
            deductions = calculate_deductions(gross, entry.deductions_config)
            net = calculate_net_salary(gross, deductions)
            payslip_data = {
                "employee_id": entry.employee_id,
                "gross_salary": gross,
                "deductions": deductions,
                "net_salary": net,
                "period": datetime.now().strftime("%B %Y"),
                "status": "generated",
                "created_at": datetime.now().isoformat(),
            }
            response = supabase.table("payroll_records").insert(payslip_data).execute()
            if response.data:
                results.append({
                    "employee_id": entry.employee_id,
                    "success": True,
                    "payslip_id": response.data[0].get("id")
                })
            else:
                results.append({"employee_id": entry.employee_id, "success": False, "error": "Insert failed"})
        except Exception as e:
            results.append({"employee_id": entry.employee_id, "success": False, "error": str(e)})

    return {
        "total": len(entries),
        "generated": sum(1 for r in results if r.get("success")),
        "results": results
    }
