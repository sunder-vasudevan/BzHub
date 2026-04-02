from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from supabase_client import supabase

router = APIRouter()

def count_employees(employees):
    return len(employees)

@router.get("/hr/employees", tags=["HR"])
def get_employees():
    response = supabase.table("employees").select("*").execute()
    employees = response.data if hasattr(response, 'data') else []
    total_employees = count_employees(employees)
    return {"employees": employees, "total_employees": total_employees}

@router.get("/hr/payroll", tags=["HR"])
def get_payrolls():
    response = (
        supabase.table("payroll")
        .select("*, employees(name)")
        .order("created_at", desc=True)
        .execute()
    )
    records = response.data if hasattr(response, "data") else []
    for r in records:
        emp = r.pop("employees", None)
        r["employee_name"] = emp.get("name") if emp else None
        # Alias to match frontend interface
        r["gross_pay"] = float(r.get("basic", 0)) + float(r.get("allowances", 0))
        r["net_pay"] = float(r.get("net", 0))
        r["period_start"] = r.get("period", "")
        r["period_end"] = ""
    return records

class PayrollCreate(BaseModel):
    employee_id: int
    period_start: str
    period_end: str
    basic: float
    allowances: float = 0.0
    deductions: float = 0.0
    status: str = "Draft"

@router.post("/hr/payroll", tags=["HR"])
def create_payroll(body: PayrollCreate):
    net = body.basic + body.allowances - body.deductions
    row = {
        "employee_id": body.employee_id,
        "period": f"{body.period_start} – {body.period_end}",
        "basic": body.basic,
        "allowances": body.allowances,
        "deductions": body.deductions,
        "net": net,
        "status": body.status,
    }
    try:
        response = supabase.table("payroll").insert(row).execute()
        return {"success": True, "record": response.data[0] if response.data else None}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
