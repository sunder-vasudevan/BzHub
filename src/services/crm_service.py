"""CRM Service — manages contacts, leads, pipeline stages, and activities."""
import logging

logger = logging.getLogger(__name__)


class CRMService:
    """Business logic layer for CRM: contacts, leads, pipeline, activities."""

    STAGES = ["New", "Contacted", "Qualified", "Proposal", "Won", "Lost"]

    def __init__(self, db_adapter):
        self.db = db_adapter

    # ------------------------------------------------------------------
    # Contacts
    # ------------------------------------------------------------------

    def add_contact(self, name: str, company: str = '', email: str = '',
                    phone: str = '', source: str = '', notes: str = '') -> int:
        """Add a new contact. Returns new id or -1 on failure."""
        if not name or not name.strip():
            logger.warning("CRMService.add_contact: name is required")
            return -1
        return self.db.add_crm_contact(
            name=name.strip(),
            company=company.strip() if company else '',
            email=email.strip() if email else '',
            phone=phone.strip() if phone else '',
            source=source.strip() if source else '',
            notes=notes.strip() if notes else '',
        )

    def get_contacts(self, search: str = None) -> list:
        """Get contacts, optionally filtered by search string."""
        return self.db.get_crm_contacts(search=search)

    def update_contact(self, contact_id: int, **kwargs) -> bool:
        """Update contact fields. Returns True on success."""
        if not contact_id:
            return False
        return self.db.update_crm_contact(contact_id, **kwargs)

    def delete_contact(self, contact_id: int) -> bool:
        """Delete a contact. Returns True on success."""
        if not contact_id:
            return False
        return self.db.delete_crm_contact(contact_id)

    # ------------------------------------------------------------------
    # Leads
    # ------------------------------------------------------------------

    def add_lead(self, contact_id: int, title: str, stage: str = 'New',
                 value: float = 0, probability: int = 0, owner: str = '', notes: str = '') -> int:
        """Add a new lead. Returns new id or -1 on failure."""
        if not title or not title.strip():
            logger.warning("CRMService.add_lead: title is required")
            return -1
        if stage not in self.STAGES:
            stage = 'New'
        try:
            value = float(value)
        except (ValueError, TypeError):
            value = 0.0
        try:
            probability = int(probability)
            probability = max(0, min(100, probability))
        except (ValueError, TypeError):
            probability = 0
        return self.db.add_crm_lead(
            contact_id=contact_id,
            title=title.strip(),
            stage=stage,
            value=value,
            probability=probability,
            owner=owner.strip() if owner else '',
            notes=notes.strip() if notes else '',
        )

    def get_leads(self, stage: str = None) -> list:
        """Get leads, optionally filtered by stage."""
        return self.db.get_crm_leads(stage=stage)

    def update_lead(self, lead_id: int, **kwargs) -> bool:
        """Update lead fields. Returns True on success."""
        if not lead_id:
            return False
        if 'stage' in kwargs and kwargs['stage'] not in self.STAGES:
            kwargs['stage'] = 'New'
        return self.db.update_crm_lead(lead_id, **kwargs)

    def delete_lead(self, lead_id: int) -> bool:
        """Delete a lead. Returns True on success."""
        if not lead_id:
            return False
        return self.db.delete_crm_lead(lead_id)

    def advance_lead_stage(self, lead_id: int, current_stage: str) -> bool:
        """Move lead to the next stage in the pipeline. Returns True on success."""
        try:
            idx = self.STAGES.index(current_stage)
            if idx < len(self.STAGES) - 1:
                next_stage = self.STAGES[idx + 1]
                return self.db.update_crm_lead(lead_id, stage=next_stage)
            return False  # Already at last stage
        except ValueError:
            return False

    # ------------------------------------------------------------------
    # Activities
    # ------------------------------------------------------------------

    def add_activity(self, lead_id: int, activity_type: str, note: str, due_date: str = '') -> bool:
        """Add an activity to a lead."""
        valid_types = ['call', 'email', 'meeting', 'note']
        if activity_type not in valid_types:
            activity_type = 'note'
        return self.db.add_crm_activity(
            lead_id=lead_id,
            activity_type=activity_type,
            note=note.strip() if note else '',
            due_date=due_date.strip() if due_date else '',
        )

    def get_activities(self, lead_id: int) -> list:
        """Get all activities for a lead."""
        return self.db.get_crm_activities(lead_id)

    def complete_activity(self, activity_id: int, done: bool = True) -> bool:
        """Mark an activity as done or not done."""
        return self.db.update_crm_activity(activity_id, done=1 if done else 0)

    # ------------------------------------------------------------------
    # Analytics
    # ------------------------------------------------------------------

    def get_pipeline_summary(self) -> dict:
        """Return a dict mapping each stage to the list of leads in that stage."""
        summary = {stage: [] for stage in self.STAGES}
        all_leads = self.db.get_crm_leads()
        for lead in all_leads:
            stage = lead[3] if len(lead) > 3 else 'New'  # index 3 = stage column
            if stage in summary:
                summary[stage].append(lead)
            else:
                summary['New'].append(lead)
        return summary

    def get_conversion_rate(self) -> float:
        """Return ratio of Won leads to total closed (Won + Lost) leads, as a percentage."""
        all_leads = self.db.get_crm_leads()
        won = sum(1 for l in all_leads if len(l) > 3 and l[3] == 'Won')
        lost = sum(1 for l in all_leads if len(l) > 3 and l[3] == 'Lost')
        total_closed = won + lost
        if total_closed == 0:
            return 0.0
        return round((won / total_closed) * 100, 1)

    def get_pipeline_value(self) -> float:
        """Return total pipeline value (sum of all non-Lost lead values)."""
        all_leads = self.db.get_crm_leads()
        total = 0.0
        for lead in all_leads:
            if len(lead) > 3 and lead[3] != 'Lost':
                try:
                    total += float(lead[4]) if len(lead) > 4 else 0  # index 4 = value
                except (ValueError, TypeError):
                    pass
        return total
