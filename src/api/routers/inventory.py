"""Inventory router — CRUD for inventory items."""
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from src.api.deps import get_inventory_service
from src.services import InventoryService

router = APIRouter()


class InventoryItem(BaseModel):
    item_name: str
    quantity: int = 0
    threshold: int = 0
    cost_price: float = 0.0
    sale_price: float = 0.0
    description: Optional[str] = None


class InventoryUpdate(BaseModel):
    quantity: Optional[int] = None
    threshold: Optional[int] = None
    cost_price: Optional[float] = None
    sale_price: Optional[float] = None
    description: Optional[str] = None


class InventoryItemResponse(BaseModel):
    id: int
    item_name: str
    quantity: int
    threshold: int
    cost_price: float
    sale_price: float
    description: Optional[str]
    image_path: Optional[str]
    updated_at: Optional[str]


def _row_to_dict(row) -> dict:
    """Convert a DB row tuple to a dict.

    get_all_inventory() returns: (item_name, quantity, threshold, cost_price, sale_price, description)
    """
    return {
        "id": row[0],           # item_name acts as unique id
        "item_name": row[0],
        "quantity": row[1],
        "threshold": row[2],
        "cost_price": float(row[3] or 0),
        "sale_price": float(row[4] or 0),
        "description": row[5] if len(row) > 5 else None,
        "image_path": row[6] if len(row) > 6 else None,
        "updated_at": row[7] if len(row) > 7 else None,
    }


@router.get("", response_model=list)
def list_inventory(
    inv_svc: InventoryService = Depends(get_inventory_service),
):
    """List all inventory items."""
    items = inv_svc.get_all_items()
    return [_row_to_dict(r) for r in items]


@router.post("", status_code=201)
def add_inventory_item(
    item: InventoryItem,
    inv_svc: InventoryService = Depends(get_inventory_service),
):
    """Add a new inventory item."""
    ok = inv_svc.add_item(
        item_name=item.item_name,
        quantity=item.quantity,
        threshold=item.threshold,
        cost_price=item.cost_price,
        sale_price=item.sale_price,
        description=item.description or "",
    )
    if not ok:
        raise HTTPException(status_code=409, detail="Item already exists or could not be added")
    return {"status": "created", "item_name": item.item_name}


@router.put("/{item_name}")
def update_inventory_item(
    item_name: str,
    updates: InventoryUpdate,
    inv_svc: InventoryService = Depends(get_inventory_service),
):
    """Update an inventory item by name."""
    kwargs = {k: v for k, v in updates.dict().items() if v is not None}
    ok = inv_svc.update_item(item_name=item_name, **kwargs)
    if not ok:
        raise HTTPException(status_code=404, detail="Item not found or update failed")
    return {"status": "updated", "item_name": item_name}


@router.delete("/{item_name}")
def delete_inventory_item(
    item_name: str,
    inv_svc: InventoryService = Depends(get_inventory_service),
):
    """Delete an inventory item by name."""
    ok = inv_svc.delete_item(item_name=item_name)
    if not ok:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"status": "deleted", "item_name": item_name}
