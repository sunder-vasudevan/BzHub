"""Visitors tab — searchable card grid of visitor/contact records."""
import tkinter as tk
from tkinter import ttk

from .base_tab import BaseTab


class VisitorsTab(BaseTab):
    """Scrollable card view of visitor records with search filtering."""

    def __init__(self, notebook: ttk.Notebook, app, tab_label: str = "👥 Visitors"):
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
        ttk.Label(header, text="👥 Visitors", style="Header.TLabel").pack(side="left")
        ttk.Label(header, text="Contacts & visits",
                  style="Subheader.TLabel").pack(side="left", padx=10)

        # Search controls
        actions = tk.Frame(header, bg=self.colors["bg"])
        actions.pack(side="right")
        self._search_var = tk.StringVar()
        ttk.Entry(actions, textvariable=self._search_var, width=24).pack(side="left", padx=(0, 6))
        ttk.Button(actions, text="Search", style="Info.TButton",
                   command=self.refresh).pack(side="left", padx=4)
        ttk.Button(actions, text="Reset", style="Info.TButton",
                   command=self._reset_search).pack(side="left")

        # Scrollable cards area
        canvas_frame = tk.Frame(container, bg=self.colors["bg"])
        canvas_frame.pack(fill="both", expand=True)

        self._canvas, self._scroll, self._cards_frame, self._canvas_window = \
            self._make_scrollable_canvas(canvas_frame)

        self.refresh()

    # ------------------------------------------------------------------
    # Data refresh
    # ------------------------------------------------------------------

    def _reset_search(self):
        self._search_var.set("")
        self.refresh()

    def refresh(self):
        if not hasattr(self, "_cards_frame"):
            return
        for w in self._cards_frame.winfo_children():
            w.destroy()

        query = (self._search_var.get() or "").strip().lower()
        visitors = self.app.visitor_service.get_all_visitors()

        filtered = [
            r for r in visitors
            if not query or any(
                query in str(v).lower()
                for v in [r[1] or "", r[3] or "", r[4] or "", r[5] or ""]
            )
        ]

        if not filtered:
            empty = tk.Frame(self._cards_frame, bg=self.colors["card"], padx=12, pady=12)
            empty.pack(fill="x", pady=6)
            tk.Label(empty, text="No visitors found",
                     bg=self.colors["card"], fg=self.colors["muted"]).pack(anchor="w")
            return

        for idx, row in enumerate(filtered):
            card = self._visitor_card(self._cards_frame, row)
            card.grid(row=idx // 2, column=idx % 2, padx=6, pady=6, sticky="nsew")

        self._cards_frame.grid_columnconfigure(0, weight=1)
        self._cards_frame.grid_columnconfigure(1, weight=1)

    # ------------------------------------------------------------------
    # Card builder
    # ------------------------------------------------------------------

    def _visitor_card(self, parent, row) -> tk.Frame:
        name    = row[1] or "—"
        address = row[2] or "—"
        phone   = row[3] or "—"
        email   = row[4] or "—"
        company = row[5] or "—"

        card = tk.Frame(parent, bg=self.colors["card"], padx=12, pady=12)

        title = tk.Frame(card, bg=self.colors["card"])
        title.pack(fill="x")
        tk.Label(title, text=name, bg=self.colors["card"], fg=self.colors["text"],
                 font=("Arial", 11, "bold")).pack(side="left")
        tk.Label(title, text=company, bg=self.colors["card"], fg=self.colors["muted"],
                 font=("Arial", 9)).pack(side="right")

        tk.Label(card, text=address, bg=self.colors["card"], fg=self.colors["muted"],
                 font=("Arial", 9)).pack(anchor="w", pady=(4, 0))

        contact = tk.Frame(card, bg=self.colors["card"])
        contact.pack(fill="x", pady=(8, 0))
        tk.Label(contact, text=f"Email: {email}", bg=self.colors["card"],
                 fg=self.colors["text"], font=("Arial", 9)).pack(anchor="w")
        tk.Label(contact, text=f"Phone: {phone}", bg=self.colors["card"],
                 fg=self.colors["text"], font=("Arial", 9)).pack(anchor="w")

        return card
