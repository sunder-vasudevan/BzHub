from fastapi import APIRouter
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
