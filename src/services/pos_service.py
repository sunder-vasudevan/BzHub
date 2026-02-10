"""Sales and POS services."""
from datetime import datetime
from src.core import POSCalculator


class POSService:
    """Handle Point of Sale operations."""
    
    def __init__(self, db_adapter):
        self.db = db_adapter
    
    def record_sale(self, item_name: str, quantity: int, sale_price: float, username: str) -> bool:
        """Record a sale transaction."""
        total_amount = quantity * sale_price
        return self.db.record_sale(item_name, quantity, sale_price, total_amount, username)
    
    def get_today_sales(self) -> list:
        """Get all sales for today."""
        today = datetime.now().strftime("%Y-%m-%d")
        return self.db.get_sales_by_date(today)
    
    def get_today_sales_total(self) -> float:
        """Calculate total sales amount for today."""
        sales = self.get_today_sales()
        return sum(sale[5] for sale in sales) if sales else 0.0
    
    def get_all_sales(self) -> list:
        """Get all sales history."""
        return self.db.get_all_sales()
    
    @staticmethod
    def calculate_total(items: list) -> float:
        """Calculate total for items (qty * price each)."""
        return POSCalculator.calculate_total(items)
    
    @staticmethod
    def apply_discount(total: float, discount_percent: float) -> float:
        """Apply discount to total."""
        return POSCalculator.apply_discount(total, discount_percent)
    
    @staticmethod
    def apply_tax(total: float, tax_percent: float) -> float:
        """Apply tax to total."""
        return POSCalculator.apply_tax(total, tax_percent)
