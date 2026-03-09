"""Dashboard tab — KPI cards, sales trend, top items, and reorder table."""
import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from src.core import CurrencyFormatter
from .base_tab import BaseTab
from . import chart_helpers as ch


class DashboardTab(BaseTab):
    """Admin dashboard with KPI cards, charts, and reorder recommendations."""

    def __init__(self, notebook: ttk.Notebook, app):
        super().__init__(notebook, app)
        self._sales_trend_data = []
        self._sales_summary_data = []
        self._build()

    # ------------------------------------------------------------------
    # Build UI
    # ------------------------------------------------------------------

    def _build(self):
        self.notebook.add(self.frame, text="📊 Dashboard")

        container = tk.Frame(self.frame, bg=self.colors["bg"])
        container.pack(fill="both", expand=True, padx=12, pady=12)

        # Header
        header = tk.Frame(container, bg=self.colors["bg"])
        header.pack(fill="x", pady=(0, 12))
        ttk.Label(header, text="📊 Dashboard", style="Header.TLabel").pack(side="left")

        period_frame = tk.Frame(header, bg=self.colors["bg"])
        period_frame.pack(side="right")
        ttk.Label(period_frame, text="Projection Window",
                  style="Subheader.TLabel").pack(side="left", padx=(0, 8))

        self._period_var = tk.StringVar(value="Last 7 Days")
        self._period_map = {
            "Last 7 Days": "7",
            "Last 30 Days": "30",
            "Quarter": "90",
            "Year": "365",
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

        # KPI cards row
        kpi_row = tk.Frame(container, bg=self.colors["bg"])
        kpi_row.pack(fill="x", pady=(0, 12))

        self._kpi = {
            "sales":          self._kpi_card(kpi_row, "Sales (Period)"),
            "inventory":      self._kpi_card(kpi_row, "Inventory Value"),
            "low_stock":      self._kpi_card(kpi_row, "Low Stock Items"),
            "visitors":       self._kpi_card(kpi_row, "Visitors"),
            "avg_daily_sales":self._kpi_card(kpi_row, "Avg Daily Sales"),
            "sales_growth":   self._kpi_card(kpi_row, "Sales Growth %"),
        }

        # Charts row
        charts_row = tk.Frame(container, bg=self.colors["bg"])
        charts_row.pack(fill="both", expand=True)

        # Sales trend chart
        sales_card = tk.Frame(charts_row, bg=self.colors["card"], padx=12, pady=12)
        sales_card.pack(side="left", fill="both", expand=True, padx=(0, 8))
        tk.Label(sales_card, text="Sales Trend", bg=self.colors["card"],
                 fg=self.colors["text"], font=("Arial", 10, "bold")).pack(anchor="w")

        self._sales_fig = Figure(figsize=(5, 3), dpi=100)
        self._sales_ax = self._sales_fig.add_subplot(111)
        self._sales_canvas = FigureCanvasTkAgg(self._sales_fig, master=sales_card)
        w = self._sales_canvas.get_tk_widget()
        w.pack(fill="both", expand=True)
        w.bind("<Configure>",
               lambda e: ch.resize_figure(e, self._sales_fig, self._sales_canvas,
                                          self.colors))
        w.bind("<Double-1>",
               lambda _e: ch.open_chart_zoom(
                   self.root, "Sales Trend",
                   lambda ax: ch.draw_sales_trend(ax, self._sales_trend_data, self.colors),
                   self.colors,
               ))

        # Top items chart
        top_card = tk.Frame(charts_row, bg=self.colors["card"], padx=12, pady=12)
        top_card.pack(side="left", fill="both", expand=True, padx=(8, 0))
        tk.Label(top_card, text="Top Selling Items", bg=self.colors["card"],
                 fg=self.colors["text"], font=("Arial", 10, "bold")).pack(anchor="w")

        self._top_fig = Figure(figsize=(5, 3), dpi=100)
        self._top_ax = self._top_fig.add_subplot(111)
        self._top_canvas = FigureCanvasTkAgg(self._top_fig, master=top_card)
        w2 = self._top_canvas.get_tk_widget()
        w2.pack(fill="both", expand=True)
        w2.bind("<Configure>",
                lambda e: ch.resize_figure(e, self._top_fig, self._top_canvas,
                                           self.colors))
        w2.bind("<Double-1>",
                lambda _e: ch.open_chart_zoom(
                    self.root, "Top Selling Items",
                    lambda ax: ch.draw_top_items(ax, self._sales_summary_data, self.colors),
                    self.colors,
                ))

        # Tables row
        tables_row = tk.Frame(container, bg=self.colors["bg"])
        tables_row.pack(fill="both", expand=True, pady=(12, 0))

        # Reorder recommendations table
        reorder_card = tk.Frame(tables_row, bg=self.colors["card"], padx=12, pady=12)
        reorder_card.pack(side="left", fill="both", expand=True, padx=(0, 8))
        tk.Label(reorder_card, text="Reorder Recommendations",
                 bg=self.colors["card"], fg=self.colors["text"],
                 font=("Arial", 10, "bold")).pack(anchor="w")

        self._reorder_tree = ttk.Treeview(
            reorder_card,
            columns=("Item", "Current", "AvgDaily", "Recommend"),
            show="headings", height=6,
        )
        for col, text, width in [
            ("Item", "Item", 160), ("Current", "Current Qty", 90),
            ("AvgDaily", "Avg Daily", 90), ("Recommend", "Recommend", 90),
        ]:
            self._reorder_tree.heading(col, text=text)
            self._reorder_tree.column(col, anchor="center", width=width)
        self._reorder_tree.pack(fill="both", expand=True, pady=(6, 0))

        # Low stock table
        low_card = tk.Frame(tables_row, bg=self.colors["card"], padx=12, pady=12)
        low_card.pack(side="left", fill="both", expand=True, padx=(8, 0))
        tk.Label(low_card, text="Low Stock Items",
                 bg=self.colors["card"], fg=self.colors["text"],
                 font=("Arial", 10, "bold")).pack(anchor="w")

        self._low_tree = ttk.Treeview(
            low_card,
            columns=("Item", "Qty", "Threshold"),
            show="headings", height=6,
        )
        for col, text, width in [
            ("Item", "Item", 180), ("Qty", "Qty", 70), ("Threshold", "Threshold", 90),
        ]:
            self._low_tree.heading(col, text=text)
            self._low_tree.column(col, anchor="center", width=width)
        self._low_tree.pack(fill="both", expand=True, pady=(6, 0))

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
        period_key = self._period_map.get(self._period_var.get(), "7")
        start_date, end_date, days = self.app.analytics_service.get_date_range(period_key)

        trend = self.app.analytics_service.get_sales_trend(start_date, end_date)
        summary = self.app.analytics_service.get_sales_summary(start_date, end_date)
        reorder = self.app.analytics_service.get_reorder_recommendations(
            start_date, end_date, window_days=7
        )

        self._sales_trend_data = trend
        self._sales_summary_data = summary

        sales_total = sum(r[1] for r in trend) if trend else 0.0
        avg_daily = (sales_total / days) if days else 0.0
        inv_value = self.app.inventory_service.get_inventory_value()
        low_stock = self.app.inventory_service.get_low_stock_items()
        visitors = self.app.visitor_service.get_total_visitors_count()

        # Growth vs previous period
        prev_end = datetime.strptime(start_date, "%Y-%m-%d") - timedelta(days=1)
        prev_start = prev_end - timedelta(days=max(1, days) - 1)
        prev_trend = self.app.analytics_service.get_sales_trend(
            prev_start.strftime("%Y-%m-%d"), prev_end.strftime("%Y-%m-%d")
        )
        prev_total = sum(r[1] for r in prev_trend) if prev_trend else 0.0
        if prev_total > 0:
            growth_text = f"{((sales_total - prev_total) / prev_total) * 100:+.1f}%"
        elif sales_total > 0:
            growth_text = "+100.0%"
        else:
            growth_text = "0.0%"

        self._kpi["sales"].config(text=CurrencyFormatter.format_currency(sales_total))
        self._kpi["inventory"].config(text=CurrencyFormatter.format_currency(inv_value))
        self._kpi["low_stock"].config(text=str(len(low_stock)))
        self._kpi["visitors"].config(text=str(visitors))
        self._kpi["avg_daily_sales"].config(text=CurrencyFormatter.format_currency(avg_daily))
        self._kpi["sales_growth"].config(text=growth_text)

        ch.draw_sales_trend(self._sales_ax, trend, self.colors)
        self._sales_fig.patch.set_facecolor(self.colors["card"])
        self._sales_canvas.draw()

        ch.draw_top_items(self._top_ax, summary, self.colors)
        self._top_fig.patch.set_facecolor(self.colors["card"])
        self._top_canvas.draw()

        # Reorder table
        for row in self._reorder_tree.get_children():
            self._reorder_tree.delete(row)
        for item_name, current_qty, avg_d, recommended in reorder:
            self._reorder_tree.insert(
                "", "end",
                values=(item_name, current_qty, f"{avg_d:.2f}", recommended),
            )

        # Low stock table
        for row in self._low_tree.get_children():
            self._low_tree.delete(row)
        for item in low_stock[:10]:
            self._low_tree.insert("", "end", values=(item[0], item[1], item[2]))
