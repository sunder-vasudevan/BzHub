"""Leads router — CRUD and pipeline summary for CRM leads."""
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from src.api.deps import get_crm_service
from src.services.crm_service import CRMService

router = APIRouter()


class LeadCreate(BaseModel):
    contact_id: Optional[int] = None
    title: str
    stage: Optional[str] = "New"
    value: Optional[float] = 0.0
    probability: Optional[int] = 0
    owner: Optional[str] = ""
    notes: Optional[str] = ""


class LeadUpdate(BaseModel):
    contact_id: Optional[int] = None
    title: Optional[str] = None
    stage: Optional[str] = None
    value: Optional[float] = None
    probability: Optional[int] = None
    owner: Optional[str] = None
    notes: Optional[str] = None


def _row_to_dict(row) -> dict:
    """Convert a crm_leads JOIN row to dict."""
    return {
        "id": row[0],
        "contact_id": row[1],
        "title": row[2],
        "stage": row[3],
        "value": row[4],
        "probability": row[5],
        "owner": row[6],
        "notes": row[7],
        "created_at": row[8] if len(row) > 8 else None,
        "updated_at": row[9] if len(row) > 9 else None,
        "contact_name": row[10] if len(row) > 10 else None,
    }


@router.get("")
def list_leads(
    stage: Optional[str] = None,
    crm_svc: CRMService = Depends(get_crm_service),
):
    """List all CRM leads, optionally filtered by stage."""
    leads = crm_svc.get_leads(stage=stage)
    return [_row_to_dict(l) for l in leads]


@router.get("/pipeline")
def get_pipeline(
    crm_svc: CRMService = Depends(get_crm_service),
):
    """Return pipeline summary grouped by stage."""
    summary = crm_svc.get_pipeline_summary()
    return {
        stage: [_row_to_dict(l) for l in leads]
        for stage, leads in summary.items()
    }


@router.post("", status_code=201)
def create_lead(
    payload: LeadCreate,
    crm_svc: CRMService = Depends(get_crm_service),
):
    """Create a new CRM lead."""
    new_id = crm_svc.add_lead(
        contact_id=payload.contact_id,
        title=payload.title,
        stage=payload.stage or "New",
        value=payload.value or 0.0,
        probability=payload.probability or 0,
        owner=payload.owner or "",
        notes=payload.notes or "",
    )
    if new_id < 0:
        raise HTTPException(status_code=400, detail="Could not create lead")
    return {"status": "created", "id": new_id}


@router.put("/{lead_id}")
def update_lead(
    lead_id: int,
    payload: LeadUpdate,
    crm_svc: CRMService = Depends(get_crm_service),
):
    """Update a CRM lead by ID."""
    kwargs = {k: v for k, v in payload.dict().items() if v is not None}
    ok = crm_svc.update_lead(lead_id, **kwargs)
    if not ok:
        raise HTTPException(status_code=404, detail="Lead not found or update failed")
    return {"status": "updated", "id": lead_id}


@router.delete("/{lead_id}")
def delete_lead(
    lead_id: int,
    crm_svc: CRMService = Depends(get_crm_service),
):
    """Delete a CRM lead by ID."""
    ok = crm_svc.delete_lead(lead_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Lead not found")
    return {"status": "deleted", "id": lead_id}
