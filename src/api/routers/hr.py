"""HR router — employees and payroll."""
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from src.api.deps import get_db
from src.db.sqlite_adapter import SQLiteAdapter

router = APIRouter()


class EmployeeCreate(BaseModel):
    name: str
    designation: Optional[str] = None
    department: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    designation: Optional[str] = None
    department: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None


def _emp_row(row) -> dict:
    keys = ["id", "emp_number", "name", "joining_date", "designation",
            "manager", "team", "email", "phone", "emergency_contact",
            "photo_path", "notes", "is_active", "created_at", "updated_at"]
    d = dict(zip(keys, row))
    d["department"] = d.pop("team", None)
    d["status"] = "Active" if d.get("is_active") else "Inactive"
    return d


def _payroll_row(row) -> dict:
    keys = ["id", "employee_id", "period_start", "period_end", "base_salary",
            "allowances", "deductions", "overtime_hours", "overtime_rate",
            "gross_pay", "net_pay", "status", "paid_date", "created_at"]
    return dict(zip(keys, row))


@router.get("/employees")
def list_employees(db: SQLiteAdapter = Depends(get_db)):
    rows = db.get_all_employees() or []
    return [_emp_row(r) for r in rows]


@router.post("/employees", status_code=201)
def create_employee(emp: EmployeeCreate, db: SQLiteAdapter = Depends(get_db)):
    ok = db.add_employee(
        name=emp.name,
        designation=emp.designation or "",
        team=emp.department or "",
        email=emp.email or "",
        phone=emp.phone or "",
    )
    if not ok:
        raise HTTPException(status_code=400, detail="Could not create employee")
    return {"status": "created"}


@router.put("/employees/{emp_id}")
def update_employee(emp_id: int, updates: EmployeeUpdate, db: SQLiteAdapter = Depends(get_db)):
    kwargs = {k: v for k, v in updates.dict().items() if v is not None}
    if "department" in kwargs:
        kwargs["team"] = kwargs.pop("department")
    ok = db.update_employee(emp_id, **kwargs)
    if not ok:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"status": "updated"}


@router.delete("/employees/{emp_id}")
def delete_employee(emp_id: int, db: SQLiteAdapter = Depends(get_db)):
    ok = db.delete_employee(emp_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"status": "deleted"}


@router.get("/payroll")
def list_payroll(db: SQLiteAdapter = Depends(get_db)):
    rows = db.get_all_payroll() or []
    return [_payroll_row(r) for r in rows]
