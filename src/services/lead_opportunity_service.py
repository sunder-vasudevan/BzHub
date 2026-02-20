# Lead/Opportunity Service for CRM

from typing import List, Optional
from src.core.lead_opportunity import LeadOpportunity

class LeadOpportunityService:
    def __init__(self, db_adapter):
        self.db = db_adapter

    def create_lead(self, lead: LeadOpportunity) -> LeadOpportunity:
        lead_dict = lead.__dict__.copy()
        lead_dict['tags'] = lead.tags or []
        lead_dict['created_at'] = lead.created_at.isoformat() if lead.created_at else None
        lead_dict['updated_at'] = lead.updated_at.isoformat() if lead.updated_at else None
        lead_id = self.db.create_lead_opportunity(lead_dict)
        lead.id = lead_id
        return lead

    def get_lead(self, lead_id: int) -> Optional[LeadOpportunity]:
        data = self.db.get_lead_opportunity(lead_id)
        if data:
            return LeadOpportunity(**data)
        return None

    def update_lead(self, lead: LeadOpportunity) -> LeadOpportunity:
        lead_dict = lead.__dict__.copy()
        lead_dict['tags'] = lead.tags or []
        lead_dict['updated_at'] = lead.updated_at.isoformat() if lead.updated_at else None
        self.db.update_lead_opportunity(lead.id, lead_dict)
        return lead

    def delete_lead(self, lead_id: int) -> bool:
        return self.db.delete_lead_opportunity(lead_id)

    def list_leads(self, filters: dict = None) -> List[LeadOpportunity]:
        data_list = self.db.list_lead_opportunities(filters)
        return [LeadOpportunity(**data) for data in data_list]
