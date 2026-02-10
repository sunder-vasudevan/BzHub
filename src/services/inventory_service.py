"""Inventory management services."""
from src.core import InventoryCalculator


class InventoryService:
    """Handle inventory operations."""
    
    def __init__(self, db_adapter):
        self.db = db_adapter
    
    def get_all_items(self) -> list:
        """Get all inventory items."""
        return self.db.get_all_inventory()
    
    def get_item(self, name: str) -> dict:
        """Get specific inventory item."""
        return self.db.get_inventory_by_name(name)
    
    def add_item(self, item_name: str, quantity: int, threshold: int,
                cost_price: float, sale_price: float, description: str = "",
                image_path: str = None) -> bool:
        """Add new inventory item."""
        if not item_name or quantity < 0 or cost_price < 0 or sale_price < 0:
            raise ValueError("Invalid inventory data")
        return self.db.add_inventory_item(item_name, quantity, threshold, cost_price, sale_price, description, image_path)
    
    def update_item(self, item_name: str, **kwargs) -> bool:
        """Update inventory item."""
        return self.db.update_inventory_item(item_name, **kwargs)
    
    def delete_item(self, item_name: str) -> bool:
        """Delete inventory item."""
        return self.db.delete_inventory_item(item_name)
    
    def search(self, query: str) -> list:
        """Search inventory by name or description."""
        return self.db.search_inventory(query)
    
    def get_low_stock_items(self) -> list:
        """Get items where quantity < threshold."""
        items = self.get_all_items()
        return InventoryCalculator.get_low_stock_items(items)
    
    def get_inventory_value(self) -> float:
        """Calculate total inventory value."""
        items = self.get_all_items()
        return InventoryCalculator.calculate_inventory_value(items)
    
    def get_total_items_count(self) -> int:
        """Get total count of items in inventory."""
        return len(self.get_all_items())
