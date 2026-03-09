"""CRM tab — container that hosts Inventory, POS, Reports, Bills, and Visitors sub-tabs."""
import tkinter as tk
from tkinter import ttk

from .base_tab import BaseTab
from .inventory_tab import InventoryTab
from .pos_tab import POSTab
from .reports_tab import ReportsTab
from .bills_tab import BillsTab
from .visitors_tab import VisitorsTab


class CRMTab(BaseTab):
    """
    CRM module container.

    Hosts a nested ttk.Notebook with:
        - Inventory  (stock management)
        - POS        (point-of-sale / cart checkout)
        - Reports    (analytics — admin only)
        - Bills      (sales timeline)
        - Visitors   (contact cards)

    Sub-tabs are accessible via:
        crm_tab.get_sub_tab("POS")           → POSTab instance
        crm_tab.crm_tab_index["Inventory"]   → frame added to the sub-notebook
        crm_tab.crm_notebook                 → the inner ttk.Notebook
    """

    def __init__(self, notebook: ttk.Notebook, app):
        super().__init__(notebook, app)
        self.crm_notebook: ttk.Notebook | None = None
        self.crm_tab_index: dict = {}
        self._sub_tabs: dict = {}
        self._build()

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def _build(self):
        self.notebook.add(self.frame, text="📇 CRM")

        container = tk.Frame(self.frame, bg=self.colors["bg"])
        container.pack(fill="both", expand=True)

        self.crm_notebook = ttk.Notebook(container)
        self.crm_notebook.pack(fill="both", expand=True)

        # Always-visible sub-tabs
        self._add_sub_tab("Inventory", InventoryTab(self.crm_notebook, self.app))
        self._add_sub_tab("POS",       POSTab(self.crm_notebook, self.app))

        # Admin-only
        if self.app.current_role == "admin":
            self._add_sub_tab("Reports", ReportsTab(self.crm_notebook, self.app))

        self._add_sub_tab("Bills",    BillsTab(self.crm_notebook, self.app))
        self._add_sub_tab("Visitors", VisitorsTab(self.crm_notebook, self.app))

    def _add_sub_tab(self, name: str, tab_instance: BaseTab):
        self._sub_tabs[name] = tab_instance
        self.crm_tab_index[name] = tab_instance.frame

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_sub_tab(self, name: str):
        """Return the tab instance for *name*, or None."""
        return self._sub_tabs.get(name)

    def select_sub_tab(self, name: str):
        """Switch the inner notebook to the named sub-tab."""
        if name in self.crm_tab_index:
            self.crm_notebook.select(self.crm_tab_index[name])
            self.crm_notebook.update_idletasks()
