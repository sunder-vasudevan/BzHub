"""Abstract database interface - allows swapping SQLite for Cloud DB."""
from abc import ABC, abstractmethod


class DatabaseAdapter(ABC):
    """Abstract interface for database operations."""
    
    # === USERS & AUTH ===
    @abstractmethod
    def create_admin_user(self, username: str, password_hash: str):
        """Create default admin user if not exists."""
        pass
    
    @abstractmethod
    def authenticate_user(self, username: str, password_hash: str) -> bool:
        """Verify user credentials."""
        pass
    
    @abstractmethod
    def get_user_role(self, username: str) -> str:
        """Get user role (admin, user, etc)."""
        pass
    
    @abstractmethod
    def update_last_login(self, username: str):
        """Update user's last login timestamp."""
        pass
    
    # === INVENTORY ===
    @abstractmethod
    def get_all_inventory(self) -> list:
        """Get all inventory items."""
        pass
    
    @abstractmethod
    def get_inventory_by_name(self, name: str) -> dict:
        """Get inventory item by name."""
        pass
    
    @abstractmethod
    def add_inventory_item(self, item_name: str, quantity: int, threshold: int, 
                          cost_price: float, sale_price: float, description: str,
                          image_path: str = None):
        """Add new inventory item."""
        pass
    
    @abstractmethod
    def update_inventory_item(self, item_name: str, quantity: int = None, 
                             threshold: int = None, cost_price: float = None,
                             sale_price: float = None, description: str = None,
                             image_path: str = None):
        """Update inventory item."""
        pass
    
    @abstractmethod
    def delete_inventory_item(self, item_name: str):
        """Delete inventory item."""
        pass
    
    @abstractmethod
    def search_inventory(self, query: str) -> list:
        """Search inventory by name or description."""
        pass
    
    # === SALES & POS ===
    @abstractmethod
    def record_sale(self, item_name: str, quantity: int, sale_price: float, 
                   total_amount: float, username: str):
        """Record a sale transaction."""
        pass
    
    @abstractmethod
    def get_sales_by_date(self, date_str: str) -> list:
        """Get all sales for a specific date."""
        pass
    
    @abstractmethod
    def get_all_sales(self) -> list:
        """Get all sales transactions."""
        pass

    @abstractmethod
    def get_sales_between(self, start_date: str, end_date: str) -> list:
        """Get all sales between start_date and end_date (inclusive)."""
        pass

    @abstractmethod
    def get_sales_summary_by_item(self, start_date: str, end_date: str) -> list:
        """Get sales summary grouped by item between dates."""
        pass

    @abstractmethod
    def get_sales_trend_by_day(self, start_date: str, end_date: str) -> list:
        """Get sales totals grouped by day between dates."""
        pass
    
    # === HR ===
    @abstractmethod
    def add_employee(self, emp_number: str, name: str, joining_date: str,
                    designation: str, manager: str, team: str, email: str,
                    phone: str, emergency_contact: str, photo_path: str, notes: str,
                    is_active: int = 1):
        """Add new employee."""
        pass
    
    @abstractmethod
    def get_all_employees(self) -> list:
        """Get all employees."""
        pass
    
    @abstractmethod
    def get_employee_by_id(self, emp_id: int) -> dict:
        """Get employee by ID."""
        pass
    
    @abstractmethod
    def update_employee(self, emp_id: int, **kwargs):
        """Update employee details."""
        pass
    
    @abstractmethod
    def delete_employee(self, emp_id: int):
        """Delete employee."""
        pass
    
    @abstractmethod
    def add_appraisal(self, employee_id: int, appraisal_date: str, rating: str, comments: str):
        """Add employee appraisal."""
        pass
    
    @abstractmethod
    def get_employee_appraisals(self, employee_id: int) -> list:
        """Get all appraisals for an employee."""
        pass
    
    @abstractmethod
    def add_goal(self, employee_id: int, goal: str, status: str, due_date: str, notes: str):
        """Add employee goal."""
        pass
    
    @abstractmethod
    def get_employee_goals(self, employee_id: int) -> list:
        """Get all goals for an employee."""
        pass
    
    # === VISITORS ===
    @abstractmethod
    def add_visitor(self, name: str, address: str, phone: str, email: str, company: str, notes: str):
        """Add new visitor."""
        pass
    
    @abstractmethod
    def get_all_visitors(self) -> list:
        """Get all visitors."""
        pass
    
    @abstractmethod
    def update_visitor(self, visitor_id: int, **kwargs):
        """Update visitor details."""
        pass
    
    @abstractmethod
    def delete_visitor(self, visitor_id: int):
        """Delete visitor."""
        pass
    
    @abstractmethod
    def search_visitors(self, query: str) -> list:
        """Search visitors by name, email, phone."""
        pass
    
    # === EMAIL CONFIG ===
    @abstractmethod
    def save_email_config(self, smtp_server: str, smtp_port: int, sender_email: str,
                         sender_password: str, recipient_email: str):
        """Save email configuration."""
        pass
    
    @abstractmethod
    def get_email_config(self) -> dict:
        """Get email configuration."""
        pass
    
    # === COMPANY INFO ===
    @abstractmethod
    def save_company_info(self, company_name: str, address: str, phone: str,
                         email: str, tax_id: str, bank_details: str):
        """Save company information."""
        pass
    
    @abstractmethod
    def get_company_info(self) -> dict:
        """Get company information."""
        pass
    
    # === ACTIVITY LOG ===
    @abstractmethod
    def log_activity(self, username: str, action: str, details: str = ""):
        """Log user activity."""
        pass
    
    @abstractmethod
    def get_activity_log(self, username: str = None) -> list:
        """Get activity log, optionally filtered by user."""
        pass

    # === PAYROLL ===
    @abstractmethod
    def add_payroll(self, employee_id: int, period_start: str, period_end: str,
                    base_salary: float, allowances: float, deductions: float,
                    overtime_hours: float, overtime_rate: float, gross_pay: float,
                    net_pay: float, status: str, paid_date: str):
        """Add payroll record."""
        pass

    @abstractmethod
    def get_all_payrolls(self) -> list:
        """Get all payroll records."""
        pass

    @abstractmethod
    def get_payrolls_by_employee(self, employee_id: int) -> list:
        """Get payroll records for an employee."""
        pass

    @abstractmethod
    def update_payroll(self, payroll_id: int, **kwargs):
        """Update payroll record."""
        pass

    @abstractmethod
    def delete_payroll(self, payroll_id: int):
        """Delete payroll record."""
        pass

    # === APPRAISALS WORKFLOW ===
    @abstractmethod
    def create_appraisal_cycle(self, employee_id: int, period_start: str, period_end: str, created_by: str = ""):
        """Create appraisal cycle."""
        pass

    @abstractmethod
    def get_all_appraisal_cycles(self) -> list:
        """Get all appraisal cycles."""
        pass

    @abstractmethod
    def update_appraisal_cycle(self, appraisal_id: int, **kwargs):
        """Update appraisal cycle."""
        pass

    @abstractmethod
    def create_feedback_request(self, appraisal_id: int, requester: str, target_employee_id: int, message: str = ""):
        """Create a 360 feedback request."""
        pass

    @abstractmethod
    def get_feedback_requests(self) -> list:
        """Get all feedback requests."""
        pass

    @abstractmethod
    def update_feedback_request(self, request_id: int, **kwargs):
        """Update feedback request."""
        pass

    @abstractmethod
    def add_feedback_entry(self, appraisal_id: int, from_employee_id: int, to_employee_id: int,
                           rating: float, feedback_text: str):
        """Add feedback entry."""
        pass

    @abstractmethod
    def get_feedback_entries(self) -> list:
        """Get all feedback entries."""
        pass
    
    @abstractmethod
    def close(self):
        """Close database connection."""
        pass
