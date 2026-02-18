from fastapi import APIRouter
from supabase_client import supabase

router = APIRouter()

def calculate_inventory_value(items):
    return sum(item.get("quantity", 0) * item.get("unit_price", 0) for item in items)

@router.get("/inventory", tags=["Inventory"])
def get_inventory():
    response = supabase.table("inventory").select("*").execute()
    items = response.data if hasattr(response, 'data') else []
    total_value = calculate_inventory_value(items)
    return {"items": items, "total_value": total_value}
