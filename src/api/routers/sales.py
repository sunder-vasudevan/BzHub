"""Sales router — list sales and checkout endpoint."""
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from src.api.deps import get_pos_service
from src.services import POSService

router = APIRouter()


class CartItem(BaseModel):
    item_name: str
    quantity: int
    sale_price: float


class CheckoutRequest(BaseModel):
    items: List[CartItem]
    username: str = "api_user"
    payment_method: str = "cash"


def _sale_row_to_dict(row) -> dict:
    """Convert a sales DB row to dict."""
    return {
        "id": row[0],
        "sale_date": str(row[1]) if len(row) > 1 else None,
        "item_name": row[2] if len(row) > 2 else None,
        "quantity": row[3] if len(row) > 3 else 0,
        "sale_price": row[4] if len(row) > 4 else 0.0,
        "total_amount": row[5] if len(row) > 5 else 0.0,
        "username": row[6] if len(row) > 6 else None,
    }


@router.get("")
def list_sales(
    pos_svc: POSService = Depends(get_pos_service),
):
    """List all sales records."""
    sales = pos_svc.get_all_sales()
    return [_sale_row_to_dict(r) for r in sales]


@router.post("/checkout")
def checkout(
    payload: CheckoutRequest,
    pos_svc: POSService = Depends(get_pos_service),
):
    """Process a checkout with a list of items."""
    if not payload.items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    results = []
    total = 0.0
    for cart_item in payload.items:
        ok = pos_svc.record_sale(
            item_name=cart_item.item_name,
            quantity=cart_item.quantity,
            sale_price=cart_item.sale_price,
            username=payload.username,
        )
        if not ok:
            raise HTTPException(
                status_code=400,
                detail=f"Could not process sale for '{cart_item.item_name}' — insufficient stock or item not found"
            )
        line_total = cart_item.quantity * cart_item.sale_price
        total += line_total
        results.append({
            "item_name": cart_item.item_name,
            "quantity": cart_item.quantity,
            "sale_price": cart_item.sale_price,
            "line_total": line_total,
        })

    return {
        "status": "success",
        "items": results,
        "total": round(total, 2),
        "payment_method": payload.payment_method,
        "timestamp": datetime.now().isoformat(),
    }
