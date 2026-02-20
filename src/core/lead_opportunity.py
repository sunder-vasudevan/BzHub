# Lead and Opportunity Data Model for CRM

from datetime import datetime
from typing import Optional, List

class LeadOpportunity:
    def __init__(
        self,
        id: int,
        name: str,
        contact_name: Optional[str] = None,
        contact_email: Optional[str] = None,
        contact_phone: Optional[str] = None,
        company: Optional[str] = None,
        stage: str = "New",
        value: float = 0.0,
        source: Optional[str] = None,
        assigned_to: Optional[str] = None,
        status: str = "active",
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        notes: Optional[str] = None,
        tags: Optional[List[str]] = None,
        score: Optional[float] = None,
    ):
        self.id = id
        self.name = name
        self.contact_name = contact_name
        self.contact_email = contact_email
        self.contact_phone = contact_phone
        self.company = company
        self.stage = stage
        self.value = value
        self.source = source
        self.assigned_to = assigned_to
        self.status = status
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        self.notes = notes
        self.tags = tags or []
        self.score = score
