"""HR management services."""
from src.core import HRCalculator


class HRService:
    """Handle HR operations."""
    
    def __init__(self, db_adapter):
        self.db = db_adapter
    
    def add_employee(self, emp_number: str, name: str, joining_date: str,
                    designation: str, manager: str = "", team: str = "",
                    email: str = "", phone: str = "", emergency_contact: str = "",
                    photo_path: str = "", notes: str = "", is_active: int = 1) -> bool:
        """Add new employee."""
        if not emp_number or not name:
            raise ValueError("Employee number and name are required")
        return self.db.add_employee(emp_number, name, joining_date, designation, manager,
                        team, email, phone, emergency_contact, photo_path, notes, is_active)
    
    def get_all_employees(self) -> list:
        """Get all employees."""
        return self.db.get_all_employees()
    
    def get_employee(self, emp_id: int) -> dict:
        """Get employee by ID."""
        return self.db.get_employee_by_id(emp_id)
    
    def update_employee(self, emp_id: int, **kwargs) -> bool:
        """Update employee details."""
        return self.db.update_employee(emp_id, **kwargs)
    
    def delete_employee(self, emp_id: int) -> bool:
        """Delete employee."""
        return self.db.delete_employee(emp_id)
    
    def get_employee_id_card_expiry(self, joining_date: str) -> str:
        """Calculate ID card expiry date."""
        return HRCalculator.calculate_id_card_expiry(joining_date)
    
    def is_employee_id_expired(self, expiry_date: str) -> bool:
        """Check if employee ID is expired."""
        return HRCalculator.is_id_expired(expiry_date)
    
    def add_appraisal(self, employee_id: int, appraisal_date: str, rating: str, comments: str = "") -> bool:
        """Add employee appraisal."""
        if not employee_id or not appraisal_date or not rating:
            raise ValueError("Employee ID, date, and rating are required")
        return self.db.add_appraisal(employee_id, appraisal_date, rating, comments)
    
    def get_employee_appraisals(self, employee_id: int) -> list:
        """Get all appraisals for employee."""
        return self.db.get_employee_appraisals(employee_id)
    
    def add_goal(self, employee_id: int, goal: str, status: str = "Not Started", due_date: str = "", notes: str = "") -> bool:
        """Add employee goal."""
        if not employee_id or not goal:
            raise ValueError("Employee ID and goal are required")
        return self.db.add_goal(employee_id, goal, status, due_date, notes)
    
    def get_employee_goals(self, employee_id: int) -> list:
        """Get all goals for employee."""
        return self.db.get_employee_goals(employee_id)
