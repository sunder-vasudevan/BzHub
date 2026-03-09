"""Shared Matplotlib chart utility functions for BizHub tabs.

All functions are stateless — they take a `colors` dict so they work
correctly in both light and dark mode without holding any reference to
the app or its state.
"""
import tkinter as tk
from datetime import datetime, timedelta

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.ticker import FixedFormatter, FixedLocator


# ---------------------------------------------------------------------------
# Figure resize helper
# ---------------------------------------------------------------------------

def resize_figure(event, figure, canvas, colors: dict):
    """Resize a Matplotlib figure to fit the current canvas widget size."""
    if event.width < 50 or event.height < 50:
        return
    dpi = figure.get_dpi()
    figure.set_size_inches(event.width / dpi, event.height / dpi, forward=False)
    font_size = max(6, min(8, int(event.height / 65)))
    for ax in figure.axes:
        ax.tick_params(axis="x", labelsize=font_size, colors=colors["text"])
        ax.tick_params(axis="y", labelsize=font_size, colors=colors["text"])
        for lbl in ax.get_xticklabels():
            lbl.set_visible(True)
            lbl.set_rotation(45)
            lbl.set_ha("right")
        ax.spines["left"].set_color(colors["border"])
        ax.spines["bottom"].set_color(colors["border"])
    figure.subplots_adjust(left=0.08, right=0.98, top=0.93, bottom=0.36)
    canvas.draw_idle()


# ---------------------------------------------------------------------------
# Axis helpers
# ---------------------------------------------------------------------------

def set_sparse_date_ticks(ax, dates: list, colors: dict):
    """Apply readable, sparse date tick labels to a trend chart x-axis."""
    if not dates:
        return
    max_labels = 8
    step = max(1, len(dates) // max_labels)
    tick_idx = list(range(0, len(dates), step))
    if tick_idx[-1] != len(dates) - 1:
        tick_idx.append(len(dates) - 1)

    tick_labels = [dates[i] for i in tick_idx]
    ax.xaxis.set_major_locator(FixedLocator(tick_idx))
    ax.xaxis.set_major_formatter(FixedFormatter(tick_labels))
    ax.tick_params(axis="x", which="both", bottom=True, top=False,
                   labelbottom=True, pad=2)
    for lbl in ax.get_xticklabels():
        lbl.set_rotation(45)
        lbl.set_ha("right")
        lbl.set_color(colors["text"])
        lbl.set_fontsize(7)
        lbl.set_visible(True)


# ---------------------------------------------------------------------------
# Chart drawing helpers
# ---------------------------------------------------------------------------

def draw_sales_trend(ax, trend: list, colors: dict):
    """Draw a sales trend line chart onto *ax*."""
    ax.clear()
    ax.set_facecolor(colors["card"])

    if trend:
        raw_dates = [d[0] for d in trend]
        dates = []
        for d in raw_dates:
            try:
                dates.append(datetime.strptime(d, "%Y-%m-%d").strftime("%m-%d"))
            except Exception:
                dates.append(str(d))
        totals = [d[1] for d in trend]
        x_pos = list(range(len(dates)))

        ax.plot(x_pos, totals, color=colors["primary"], linewidth=2,
                marker="o", markersize=4, markerfacecolor=colors["primary"])
        ax.fill_between(x_pos, totals, color=colors["accent"], alpha=0.2)
        set_sparse_date_ticks(ax, dates, colors)
        ax.set_xlim(-0.5, len(dates) - 0.5)
        ax.xaxis.set_ticks_position("bottom")
        ax.tick_params(axis="x", labelsize=8, colors=colors["text"])
        ax.tick_params(axis="y", labelsize=8, colors=colors["text"])
        ax.grid(axis="y", color=colors["border"], alpha=0.5, linestyle="--", linewidth=0.8)
        ax.margins(x=0.02)

        if totals:
            last = len(totals) - 1
            ax.annotate(
                f"{totals[last]:.0f}", (x_pos[last], totals[last]),
                textcoords="offset points", xytext=(0, 8),
                ha="center", fontsize=8, color=colors["text"],
            )
    else:
        dates = [
            (datetime.now().date() - timedelta(days=i)).strftime("%m-%d")
            for i in range(6, -1, -1)
        ]
        x_pos = list(range(len(dates)))
        totals = [0] * len(dates)
        ax.plot(x_pos, totals, color=colors["primary"], linewidth=1.5, alpha=0.6)
        set_sparse_date_ticks(ax, dates, colors)
        ax.set_xlim(-0.5, len(dates) - 0.5)
        ax.xaxis.set_ticks_position("bottom")
        ax.tick_params(axis="x", labelsize=7, colors=colors["text"])
        ax.tick_params(axis="y", labelsize=7, colors=colors["text"])
        ax.grid(axis="y", color=colors["border"], alpha=0.4, linestyle="--", linewidth=0.8)
        ax.text(0.5, 0.6, "No sales data", color=colors["muted"],
                ha="center", va="center", transform=ax.transAxes)

    ax.set_xlabel("Date", color=colors["muted"], fontsize=8)
    ax.set_ylabel("Sales", color=colors["muted"], fontsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(colors["border"])
    ax.spines["bottom"].set_color(colors["border"])


def draw_top_items(ax, summary: list, colors: dict):
    """Draw a horizontal bar chart of top-selling items onto *ax*."""
    ax.clear()
    ax.set_facecolor(colors["card"])
    top = summary[:5] if summary else []

    if top:
        labels = [i[0] for i in top]
        qtys = [i[1] for i in top]
        bars = ax.barh(labels, qtys, color=colors["primary"])
        ax.tick_params(axis="x", labelsize=8, colors=colors["text"])
        ax.tick_params(axis="y", labelsize=8, colors=colors["text"])
        ax.grid(axis="x", color=colors["border"], alpha=0.5, linestyle="--", linewidth=0.8)
        for bar, qty in zip(bars, qtys):
            ax.text(bar.get_width() + 0.1,
                    bar.get_y() + bar.get_height() / 2,
                    str(qty), va="center", ha="left",
                    fontsize=8, color=colors["text"])
    else:
        ax.text(0.5, 0.5, "No sales data", color=colors["muted"],
                ha="center", va="center")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(colors["border"])
    ax.spines["bottom"].set_color(colors["border"])


# ---------------------------------------------------------------------------
# Zoom window
# ---------------------------------------------------------------------------

def open_chart_zoom(root, title: str, draw_fn, colors: dict):
    """Open an enlarged interactive chart window. Click anywhere to close."""
    zoom = tk.Toplevel(root)
    zoom.title(title)
    zoom.geometry("900x600")
    zoom.minsize(700, 500)

    frame = tk.Frame(zoom, bg=colors["bg"])
    frame.pack(fill="both", expand=True, padx=12, pady=12)
    tk.Label(frame, text=title, bg=colors["bg"], fg=colors["text"],
             font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 8))

    fig = Figure(figsize=(7, 4), dpi=100)
    ax = fig.add_subplot(111)
    draw_fn(ax)
    fig.patch.set_facecolor(colors["card"])
    fig.subplots_adjust(left=0.08, right=0.98, top=0.93, bottom=0.36)

    ax.xaxis.set_visible(True)
    ax.spines["bottom"].set_visible(True)
    ax.tick_params(axis="x", which="both", bottom=True, top=False, labelbottom=True)
    for lbl in ax.get_xticklabels():
        lbl.set_visible(True)

    canvas = FigureCanvasTkAgg(fig, master=frame)
    widget = canvas.get_tk_widget()
    widget.pack(fill="both", expand=True)
    widget.bind("<Configure>", lambda e: resize_figure(e, fig, canvas, colors))
    widget.bind("<Button-1>", lambda _e: zoom.destroy())
    canvas.draw()
