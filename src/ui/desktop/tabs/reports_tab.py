"""Reports tab — period-based analytics with KPI cards and charts."""
import tkinter as tk
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from src.core import CurrencyFormatter
from .base_tab import BaseTab
from . import chart_helpers as ch


class ReportsTab(BaseTab):
    """Admin-only sales reports with trend line and top-items charts."""

    def __init__(self, notebook: ttk.Notebook, app, tab_label: str = "📊 Reports"):
        super().__init__(notebook, app)
        self._tab_label = tab_label
        self._trend_data = []
        self._summary_data = []
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
        ttk.Label(header, text="📈 Reports", style="Header.TLabel").pack(side="left")
        ttk.Label(header, text="Sales insights and performance",
                  style="Subheader.TLabel").pack(side="left", padx=10)

        period_frame = tk.Frame(header, bg=self.colors["bg"])
        period_frame.pack(side="right")
        ttk.Label(period_frame, text="Time Range",
                  style="Subheader.TLabel").pack(side="left", padx=(0, 8))

        self._period_var = tk.StringVar(value="Last 30 Days")
        self._period_map = {
            "Last 7 Days":  "7",
            "Last 30 Days": "30",
            "Quarter":      "90",
            "Year":         "365",
        }
        self._period_combo = ttk.Combobox(
            period_frame,
            values=list(self._period_map.keys()),
            textvariable=self._period_var,
            state="readonly",
            width=16,
        )
        self._period_combo.pack(side="left")
        self._period_combo.bind("<<ComboboxSelected>>", lambda _e: self.refresh())

        # KPI cards
        cards_row = tk.Frame(container, bg=self.colors["bg"])
        cards_row.pack(fill="x", pady=(0, 12))

        self._kpi = {
            "total_sales": self._kpi_card(cards_row, "Total Sales"),
            "avg_daily":   self._kpi_card(cards_row, "Avg Daily Sales"),
            "top_item":    self._kpi_card(cards_row, "Top Item"),
            "items_sold":  self._kpi_card(cards_row, "Items Sold"),
        }

        # Charts
        charts_row = tk.Frame(container, bg=self.colors["bg"])
        charts_row.pack(fill="both", expand=True)

        trend_card = tk.Frame(charts_row, bg=self.colors["card"], padx=12, pady=12)
        trend_card.pack(side="left", fill="both", expand=True, padx=(0, 8))
        tk.Label(trend_card, text="Sales Trend", bg=self.colors["card"],
                 fg=self.colors["text"], font=("Arial", 10, "bold")).pack(anchor="w")

        self._sales_fig = Figure(figsize=(5, 3), dpi=100)
        self._sales_ax  = self._sales_fig.add_subplot(111)
        self._sales_canvas = FigureCanvasTkAgg(self._sales_fig, master=trend_card)
        w = self._sales_canvas.get_tk_widget()
        w.pack(fill="both", expand=True)
        w.bind("<Configure>",
               lambda e: ch.resize_figure(e, self._sales_fig, self._sales_canvas, self.colors))
        w.bind("<Double-1>",
               lambda _e: ch.open_chart_zoom(
                   self.root, "Sales Trend",
                   lambda ax: ch.draw_sales_trend(ax, self._trend_data, self.colors),
                   self.colors,
               ))

        items_card = tk.Frame(charts_row, bg=self.colors["card"], padx=12, pady=12)
        items_card.pack(side="left", fill="both", expand=True, padx=(8, 0))
        tk.Label(items_card, text="Top Items", bg=self.colors["card"],
                 fg=self.colors["text"], font=("Arial", 10, "bold")).pack(anchor="w")

        self._items_fig = Figure(figsize=(5, 3), dpi=100)
        self._items_ax  = self._items_fig.add_subplot(111)
        self._items_canvas = FigureCanvasTkAgg(self._items_fig, master=items_card)
        w2 = self._items_canvas.get_tk_widget()
        w2.pack(fill="both", expand=True)
        w2.bind("<Configure>",
                lambda e: ch.resize_figure(e, self._items_fig, self._items_canvas, self.colors))
        w2.bind("<Double-1>",
                lambda _e: ch.open_chart_zoom(
                    self.root, "Top Items",
                    lambda ax: ch.draw_top_items(ax, self._summary_data, self.colors),
                    self.colors,
                ))

        self.refresh()

    # ------------------------------------------------------------------
    # KPI card helper
    # ------------------------------------------------------------------

    def _kpi_card(self, parent, title: str) -> tk.Label:
        card = tk.Frame(parent, bg=self.colors["card"], padx=12, pady=12)
        card.pack(side="left", fill="both", expand=True, padx=6)
        tk.Label(card, text=title, bg=self.colors["card"],
                 fg=self.colors["muted"], font=("Arial", 9)).pack(anchor="w")
        lbl = tk.Label(card, text="--", bg=self.colors["card"],
                       fg=self.colors["text"], font=("Arial", 16, "bold"))
        lbl.pack(anchor="w", pady=(6, 0))
        return lbl

    # ------------------------------------------------------------------
    # Data refresh
    # ------------------------------------------------------------------

    def refresh(self):
        period_key = self._period_map.get(self._period_var.get(), "30")
        start_date, end_date, days = self.app.analytics_service.get_date_range(period_key)

        trend   = self.app.analytics_service.get_sales_trend(start_date, end_date)
        summary = self.app.analytics_service.get_sales_summary(start_date, end_date)

        self._trend_data   = trend
        self._summary_data = summary

        total_sales  = sum(r[1] for r in trend)   if trend   else 0.0
        avg_daily    = total_sales / max(1, days)
        items_sold   = sum(r[1] for r in summary) if summary else 0
        top_item     = summary[0][0]              if summary else "—"

        self._kpi["total_sales"].config(text=CurrencyFormatter.format_currency(total_sales))
        self._kpi["avg_daily"].config(text=CurrencyFormatter.format_currency(avg_daily))
        self._kpi["items_sold"].config(text=str(items_sold))
        self._kpi["top_item"].config(text=top_item)

        ch.draw_sales_trend(self._sales_ax, trend, self.colors)
        self._sales_fig.patch.set_facecolor(self.colors["card"])
        self._sales_canvas.draw()

        ch.draw_top_items(self._items_ax, summary, self.colors)
        self._items_fig.patch.set_facecolor(self.colors["card"])
        self._items_canvas.draw()
