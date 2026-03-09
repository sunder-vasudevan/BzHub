"""BizHub UI tab modules.

Each tab is a self-contained class that inherits from BaseTab.
New tabs should:
    1. Create a subclass of BaseTab
    2. Call self.notebook.add(self.frame, text="...") in _build()
    3. Implement refresh() for on-demand data reload
    4. Access services via self.app.<service_name>
    5. Register in crm_tab.py or bizhub_desktop.py as appropriate
"""
from .base_tab import BaseTab
from .chart_helpers import (
    resize_figure,
    set_sparse_date_ticks,
    draw_sales_trend,
    draw_top_items,
    open_chart_zoom,
)
from .dashboard_tab import DashboardTab
from .inventory_tab import InventoryTab
from .pos_tab import POSTab
from .bills_tab import BillsTab
from .reports_tab import ReportsTab
from .visitors_tab import VisitorsTab
from .hr_tab import HRTab
from .settings_tab import SettingsTab
from .crm_tab import CRMTab

__all__ = [
    "BaseTab",
    "DashboardTab",
    "InventoryTab",
    "POSTab",
    "BillsTab",
    "ReportsTab",
    "VisitorsTab",
    "HRTab",
    "SettingsTab",
    "CRMTab",
    # chart helpers (re-exported for convenience)
    "resize_figure",
    "set_sparse_date_ticks",
    "draw_sales_trend",
    "draw_top_items",
    "open_chart_zoom",
]
