"""Core business logic - Pure Python, no dependencies on DB or UI."""
import hashlib
from datetime import datetime, timedelta


class PasswordManager:
    """Handle password hashing and verification."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify a password against its hash."""
        return PasswordManager.hash_password(password) == password_hash


class CurrencyFormatter:
    """Format currency values."""
    
    @staticmethod
    def format_currency(value: float, symbol: str = "₹") -> str:
        """Format a number as currency."""
        try:
            return f"{symbol}{float(value):.2f}"
        except (ValueError, TypeError):
            return f"{symbol}0.00"


class InventoryCalculator:
    """Core inventory calculations - no DB dependencies."""
    
    @staticmethod
    def _get_value(item, key: str, index: int, default=0):
        """Get value from item (handles dict, tuple, or object)."""
        if isinstance(item, dict):
            return item.get(key, default)
        elif isinstance(item, (list, tuple)):
            return item[index] if len(item) > index else default
        else:
            return getattr(item, key, default)
    
    @staticmethod
    def calculate_inventory_value(items: list) -> float:
        """Calculate total inventory value (qty * cost_price).
        Items can be tuples: (item_name, quantity, threshold, cost_price, sale_price, description)
        """
        total = 0.0
        for item in items:
            qty = InventoryCalculator._get_value(item, 'quantity', 1, 0)
            cost = InventoryCalculator._get_value(item, 'cost_price', 3, 0)
            total += qty * cost
        return total
    
    @staticmethod
    def get_low_stock_items(items: list) -> list:
        """Return items where quantity < threshold.
        Items can be tuples: (item_name, quantity, threshold, cost_price, sale_price, description)
        """
        low_stock = []
        for item in items:
            qty = InventoryCalculator._get_value(item, 'quantity', 1, 0)
            threshold = InventoryCalculator._get_value(item, 'threshold', 2, 0)
            if qty < threshold:
                low_stock.append(item)
        return low_stock


class POSCalculator:
    """Core POS transaction calculations."""
    
    @staticmethod
    def calculate_total(items: list) -> float:
        """Calculate total sale amount from items."""
        total = 0.0
        for item in items:
            qty = item.get('quantity', 0) if isinstance(item, dict) else getattr(item, 'quantity', 0)
            price = item.get('sale_price', 0) if isinstance(item, dict) else getattr(item, 'sale_price', 0)
            total += qty * price
        return total
    
    @staticmethod
    def apply_discount(total: float, discount_percent: float) -> float:
        """Apply percentage discount to total."""
        if not 0 <= discount_percent <= 100:
            raise ValueError("Discount percent must be between 0 and 100")
        return total * (1 - discount_percent / 100)
    
    @staticmethod
    def apply_tax(total: float, tax_percent: float) -> float:
        """Apply percentage tax to total."""
        if not tax_percent >= 0:
            raise ValueError("Tax percent cannot be negative")
        return total * (1 + tax_percent / 100)


class HRCalculator:
    """Core HR calculations."""
    
    @staticmethod
    def calculate_id_card_expiry(joining_date_str: str, validity_years: int = 1) -> str:
        """Calculate ID card expiry date (joining_date + validity_years)."""
        try:
            joining_date = datetime.strptime(joining_date_str, "%Y-%m-%d")
            expiry_date = joining_date + timedelta(days=365 * validity_years)
            return expiry_date.strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            return ""
    
    @staticmethod
    def is_id_expired(expiry_date_str: str) -> bool:
        """Check if ID card is expired."""
        try:
            expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d")
            return datetime.now() > expiry_date
        except (ValueError, TypeError):
            return False


class BillNameGenerator:
    """Generate bill filenames with proper format."""
    
    @staticmethod
    def generate_bill_filename(bill_type: str = 'bill') -> str:
        """Generate bill filename: bill_DDMMYYYY_HHMMSS.txt"""
        now = datetime.now()
        timestamp = now.strftime("%d%m%Y_%H%M%S")
        return f"{bill_type}_{timestamp}.txt"


class DataValidator:
    """Validate input data."""
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Basic email validation."""
        return '@' in email and '.' in email.split('@')[1]
    
    @staticmethod
    def is_valid_phone(phone: str) -> bool:
        """Basic phone validation (at least 7 digits)."""
        digits = ''.join(filter(str.isdigit, phone))
        return len(digits) >= 7
    
    @staticmethod
    def sanitize_input(value: str) -> str:
        """Sanitize user input."""
        if not isinstance(value, str):
            return str(value)
        return value.strip()
