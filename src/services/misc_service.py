"""Activity and audit logging services."""


class ActivityService:
    """Handle activity logging."""
    
    def __init__(self, db_adapter):
        self.db = db_adapter
    
    def log(self, username: str, action: str, details: str = ""):
        """Log user activity."""
        self.db.log_activity(username, action, details)
    
    def get_activity_log(self, username: str = None) -> list:
        """Get activity log."""
        return self.db.get_activity_log(username)


class CompanyService:
    """Handle company information."""
    
    def __init__(self, db_adapter):
        self.db = db_adapter
    
    def save_info(self, company_name: str, address: str = "", phone: str = "",
                 email: str = "", tax_id: str = "", bank_details: str = "") -> bool:
        """Save company information."""
        return self.db.save_company_info(company_name, address, phone, email, tax_id, bank_details)
    
    def get_info(self) -> dict:
        """Get company information."""
        return self.db.get_company_info()
