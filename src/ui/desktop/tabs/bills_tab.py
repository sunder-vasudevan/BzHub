"""Bills tab — scrollable timeline of sales history with receipt printing."""
import tkinter as tk
from tkinter import ttk

from src.core import CurrencyFormatter
from .base_tab import BaseTab


class BillsTab(BaseTab):
    """Chronological timeline of all sales, grouped by date."""

    def __init__(self, notebook: ttk.Notebook, app, tab_label: str = "📋 Bills"):
        super().__init__(notebook, app)
        self._tab_label = tab_label
        self._build()

    # ------------------------------------------------------------------
    # Build UI
    # ------------------------------------------------------------------

    def _build(self):
        self.notebook.add(self.frame, text=self._tab_label)

        container = tk.Frame(self.frame, bg=self.colors["bg"])
        container.pack(fill="both", expand=True, padx=12, pady=12)

        header = tk.Frame(container, bg=self.colors["bg"])
        header.pack(fill="x", pady=(0, 12))
        ttk.Label(header, text="🧾 Bills Timeline", style="Header.TLabel").pack(side="left")
        ttk.Label(header, text="Recent sales history",
                  style="Subheader.TLabel").pack(side="left", padx=10)

        # Scrollable timeline
        canvas_frame = tk.Frame(container, bg=self.colors["bg"])
        canvas_frame.pack(fill="both", expand=True)

        self._canvas, self._scroll, self._timeline_frame, self._canvas_window = \
            self._make_scrollable_canvas(canvas_frame)

        self.refresh()

    # ------------------------------------------------------------------
    # Data refresh
    # ------------------------------------------------------------------

    def refresh(self):
        if not hasattr(self, "_timeline_frame"):
            return
        for w in self._timeline_frame.winfo_children():
            w.destroy()

        sales = self.app.pos_service.get_all_sales()
        if not sales:
            empty = tk.Frame(self._timeline_frame, bg=self.colors["card"], padx=12, pady=12)
            empty.pack(fill="x", pady=6)
            tk.Label(empty, text="No sales history yet",
                     bg=self.colors["card"], fg=self.colors["muted"]).pack(anchor="w")
            return

        # Group by date
        grouped: dict = {}
        for row in sales:
            day = str(row[1])[:10]
            grouped.setdefault(day, []).append(row)

        for day in sorted(grouped.keys(), reverse=True):
            day_card = tk.Frame(self._timeline_frame, bg=self.colors["card"], padx=12, pady=10)
            day_card.pack(fill="x", pady=6)

            tk.Label(day_card, text=day, bg=self.colors["card"],
                     fg=self.colors["text"], font=("Arial", 10, "bold")).pack(anchor="w")

            for row in grouped[day]:
                _, sale_date, item_name, qty, sale_price, total_amount, username = row
                entry = tk.Frame(day_card, bg=self.colors["card"])
                entry.pack(fill="x", pady=4)

                left = tk.Frame(entry, bg=self.colors["card"])
                left.pack(side="left", fill="x", expand=True)
                tk.Label(left, text=item_name, bg=self.colors["card"],
                         fg=self.colors["text"], font=("Arial", 9, "bold")).pack(anchor="w")
                tk.Label(left, text=f"Qty: {qty} • By: {username}",
                         bg=self.colors["card"], fg=self.colors["muted"],
                         font=("Arial", 9)).pack(anchor="w")

                right_col = tk.Frame(entry, bg=self.colors["card"])
                right_col.pack(side="right")
                tk.Label(right_col,
                         text=CurrencyFormatter.format_currency(total_amount),
                         bg=self.colors["card"], fg=self.colors["text"],
                         font=("Arial", 9, "bold")).pack(anchor="e")
                tk.Label(right_col, text=str(sale_date)[11:16],
                         bg=self.colors["card"], fg=self.colors["muted"],
                         font=("Arial", 8)).pack(anchor="e")
                ttk.Button(
                    right_col, text="Print", style="Info.TButton",
                    command=lambda r=row: self._print_sale(r),
                ).pack(anchor="e", pady=(4, 0))

    # ------------------------------------------------------------------
    # Print helper — delegates to POSTab
    # ------------------------------------------------------------------

    def _print_sale(self, sale_row):
        pos_tab = self.app.pos_tab
        if pos_tab:
            pos_tab.print_sale_receipt(sale_row)
