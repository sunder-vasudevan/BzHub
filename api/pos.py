from fastapi import APIRouter
from supabase_client import supabase

router = APIRouter()

def calculate_total_sales(transactions):
    return sum(txn.get("amount", 0) for txn in transactions)

@router.get("/pos/transactions", tags=["POS"])
def get_transactions():
    response = supabase.table("transactions").select("*").execute()
    transactions = response.data if hasattr(response, 'data') else []
    total_sales = calculate_total_sales(transactions)
    return {"transactions": transactions, "total_sales": total_sales}
