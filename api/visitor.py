from fastapi import APIRouter
from supabase_client import supabase

router = APIRouter()

# Example endpoint: Get all visitors
data = [
    {"id": 1, "name": "Charlie", "purpose": "Meeting"},
    {"id": 2, "name": "Dana", "purpose": "Delivery"},
]

def count_visitors(visitors):
    return len(visitors)

@router.get("/visitors", tags=["Visitor"])
def get_visitors():
    response = supabase.table("visitors").select("*").execute()
    visitors = response.data if hasattr(response, 'data') else []
    total_visitors = count_visitors(visitors)
    return {"visitors": visitors, "total_visitors": total_visitors}
