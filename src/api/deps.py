"""Shared FastAPI dependencies — DB adapter and service instances."""
import os
import sys

# Ensure project root is in path
_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if _root not in sys.path:
    sys.path.insert(0, _root)

from src.db.sqlite_adapter import SQLiteAdapter
from src.services import (
    AuthService, InventoryService, POSService, VisitorService,
    AnalyticsService, CRMService,
)

DB_FILE = os.getenv("DB_FILE", "inventory.db")

# Single shared DB adapter for the API process
_db = SQLiteAdapter(DB_FILE)

# Shared service instances
auth_service = AuthService(_db)
inventory_service = InventoryService(_db)
pos_service = POSService(_db)
visitor_service = VisitorService(_db)
analytics_service = AnalyticsService(_db)
crm_service = CRMService(_db)


def get_db() -> SQLiteAdapter:
    """FastAPI dependency that returns the shared DB adapter."""
    return _db


def get_auth_service() -> AuthService:
    return auth_service


def get_inventory_service() -> InventoryService:
    return inventory_service


def get_pos_service() -> POSService:
    return pos_service


def get_visitor_service() -> VisitorService:
    return visitor_service


def get_analytics_service() -> AnalyticsService:
    return analytics_service


def get_crm_service() -> CRMService:
    return crm_service
