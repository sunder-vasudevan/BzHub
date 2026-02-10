"""Appraisal workflow services."""


class AppraisalService:
    """Handle appraisals, 360 requests, and feedback entries."""

    def __init__(self, db_adapter):
        self.db = db_adapter

    def create_appraisal(self, employee_id: int, period_start: str, period_end: str, created_by: str = "") -> bool:
        return self.db.create_appraisal_cycle(employee_id, period_start, period_end, created_by)

    def get_all_appraisals(self) -> list:
        return self.db.get_all_appraisal_cycles()

    def update_self_appraisal(self, appraisal_id: int, text: str, rating: float) -> bool:
        return self.db.update_appraisal_cycle(appraisal_id, self_text=text, self_rating=rating, status="Self Submitted")

    def update_manager_review(self, appraisal_id: int, text: str, rating: float) -> bool:
        return self.db.update_appraisal_cycle(appraisal_id, manager_text=text, manager_rating=rating, status="Manager Reviewed")

    def finalize_appraisal(self, appraisal_id: int, final_rating: float) -> bool:
        return self.db.update_appraisal_cycle(appraisal_id, final_rating=final_rating, status="Finalized")

    def update_appraisal_fields(self, appraisal_id: int, **kwargs) -> bool:
        return self.db.update_appraisal_cycle(appraisal_id, **kwargs)

    def create_feedback_request(self, appraisal_id: int, requester: str, target_employee_id: int, message: str = "") -> bool:
        return self.db.create_feedback_request(appraisal_id, requester, target_employee_id, message)

    def get_feedback_requests(self) -> list:
        return self.db.get_feedback_requests()

    def update_feedback_request_status(self, request_id: int, status: str) -> bool:
        return self.db.update_feedback_request(request_id, status=status)

    def add_feedback_entry(self, appraisal_id: int, from_employee_id: int, to_employee_id: int,
                           rating: float, feedback_text: str) -> bool:
        return self.db.add_feedback_entry(appraisal_id, from_employee_id, to_employee_id, rating, feedback_text)

    def get_feedback_entries(self) -> list:
        return self.db.get_feedback_entries()
