"""Contacts router — CRUD for CRM contacts."""
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from src.api.deps import get_crm_service
from src.services.crm_service import CRMService

router = APIRouter()


class ContactCreate(BaseModel):
    name: str
    company: Optional[str] = ""
    email: Optional[str] = ""
    phone: Optional[str] = ""
    source: Optional[str] = ""
    notes: Optional[str] = ""


class ContactUpdate(BaseModel):
    name: Optional[str] = None
    company: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    source: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None


def _row_to_dict(row) -> dict:
    """Convert a crm_contacts row to dict."""
    return {
        "id": row[0],
        "name": row[1],
        "company": row[2],
        "email": row[3],
        "phone": row[4],
        "source": row[5],
        "status": row[6],
        "notes": row[7],
        "created_at": row[8] if len(row) > 8 else None,
    }


@router.get("")
def list_contacts(
    search: Optional[str] = None,
    crm_svc: CRMService = Depends(get_crm_service),
):
    """List all CRM contacts, optionally filtered by search string."""
    contacts = crm_svc.get_contacts(search=search)
    return [_row_to_dict(c) for c in contacts]


@router.post("", status_code=201)
def create_contact(
    payload: ContactCreate,
    crm_svc: CRMService = Depends(get_crm_service),
):
    """Create a new CRM contact."""
    new_id = crm_svc.add_contact(
        name=payload.name,
        company=payload.company or "",
        email=payload.email or "",
        phone=payload.phone or "",
        source=payload.source or "",
        notes=payload.notes or "",
    )
    if new_id < 0:
        raise HTTPException(status_code=400, detail="Could not create contact")
    return {"status": "created", "id": new_id}


@router.put("/{contact_id}")
def update_contact(
    contact_id: int,
    payload: ContactUpdate,
    crm_svc: CRMService = Depends(get_crm_service),
):
    """Update a CRM contact by ID."""
    kwargs = {k: v for k, v in payload.dict().items() if v is not None}
    ok = crm_svc.update_contact(contact_id, **kwargs)
    if not ok:
        raise HTTPException(status_code=404, detail="Contact not found or update failed")
    return {"status": "updated", "id": contact_id}


@router.delete("/{contact_id}")
def delete_contact(
    contact_id: int,
    crm_svc: CRMService = Depends(get_crm_service),
):
    """Delete a CRM contact by ID."""
    ok = crm_svc.delete_contact(contact_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Contact not found")
    return {"status": "deleted", "id": contact_id}
