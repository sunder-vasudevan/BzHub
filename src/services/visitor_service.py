"""Visitor management services."""


class VisitorService:
    """Handle visitor management."""
    
    def __init__(self, db_adapter):
        self.db = db_adapter
    
    def add_visitor(self, name: str, address: str = "", phone: str = "",
                   email: str = "", company: str = "", notes: str = "") -> bool:
        """Add new visitor."""
        if not name:
            raise ValueError("Visitor name is required")
        return self.db.add_visitor(name, address, phone, email, company, notes)
    
    def get_all_visitors(self) -> list:
        """Get all visitors."""
        return self.db.get_all_visitors()
    
    def update_visitor(self, visitor_id: int, **kwargs) -> bool:
        """Update visitor details."""
        return self.db.update_visitor(visitor_id, **kwargs)
    
    def delete_visitor(self, visitor_id: int) -> bool:
        """Delete visitor."""
        return self.db.delete_visitor(visitor_id)
    
    def search(self, query: str) -> list:
        """Search visitors."""
        return self.db.search_visitors(query)
    
    def get_total_visitors_count(self) -> int:
        """Get total count of visitors."""
        return len(self.get_all_visitors())
