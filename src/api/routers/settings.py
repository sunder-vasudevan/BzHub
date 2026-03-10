"""Settings router — company profile."""
from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from src.api.deps import get_db
from src.db.sqlite_adapter import SQLiteAdapter

router = APIRouter()


class CompanySettings(BaseModel):
    company_name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None


@router.get("/company")
def get_company(db: SQLiteAdapter = Depends(get_db)):
    info = db.get_company_info() or {}
    if isinstance(info, (list, tuple)) and len(info) > 0:
        row = info[0] if isinstance(info, list) else info
        keys = ["id", "company_name", "address", "phone", "email", "website",
                "tax_id", "currency", "logo_path", "created_at", "updated_at"]
        info = dict(zip(keys, row))
    return info or {}


@router.post("/company")
def save_company(data: CompanySettings, db: SQLiteAdapter = Depends(get_db)):
    kwargs = {k: v for k, v in data.dict().items() if v is not None}
    db.update_company_info(**kwargs)
    return {"status": "saved"}
