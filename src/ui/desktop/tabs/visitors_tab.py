"""Visitors tab — searchable card grid of visitor/contact records with full CRUD."""
import tkinter as tk
from tkinter import ttk, messagebox

from .base_tab import BaseTab


class VisitorsTab(BaseTab):
    """Scrollable card view of visitor records with search, add, edit, and delete."""

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

        # Header row
        header = tk.Frame(container, bg=self.colors["bg"])
        header.pack(fill="x", pady=(0, 12))
        ttk.Label(header, text="👥 Visitors", style="Header.TLabel").pack(side="left")
        ttk.Label(header, text="Contacts & visits",
                  style="Subheader.TLabel").pack(side="left", padx=10)

        actions = tk.Frame(header, bg=self.colors["bg"])
        actions.pack(side="right")
        ttk.Button(actions, text="+ New Contact", style="Success.TButton",
                   command=self._open_add_form).pack(side="left", padx=(0, 10))
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
    # Search
    # ------------------------------------------------------------------

    def _reset_search(self):
        self._search_var.set("")
        self.refresh()

    # ------------------------------------------------------------------
    # Data refresh
    # ------------------------------------------------------------------

    def refresh(self):
        if not hasattr(self, "_cards_frame"):
            return
        for w in self._cards_frame.winfo_children():
            w.destroy()

        query    = (self._search_var.get() or "").strip().lower()
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
            tk.Label(empty, text="No contacts found",
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
        visitor_id = row[0]
        name    = row[1] or "—"
        address = row[2] or "—"
        phone   = row[3] or "—"
        email   = row[4] or "—"
        company = row[5] or "—"

        card = tk.Frame(parent, bg=self.colors["card"], padx=12, pady=12)

        # Title row: name + company
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
        tk.Label(contact, text=f"✉  {email}", bg=self.colors["card"],
                 fg=self.colors["text"], font=("Arial", 9)).pack(anchor="w")
        tk.Label(contact, text=f"📞 {phone}", bg=self.colors["card"],
                 fg=self.colors["text"], font=("Arial", 9)).pack(anchor="w")

        # Edit / Delete buttons
        btn_row = tk.Frame(card, bg=self.colors["card"])
        btn_row.pack(fill="x", pady=(10, 0))
        ttk.Button(btn_row, text="Edit", style="Info.TButton",
                   command=lambda: self._open_edit_form(row)).pack(side="left", padx=(0, 6))
        ttk.Button(btn_row, text="Delete", style="Danger.TButton",
                   command=lambda: self._delete_contact(visitor_id, name)).pack(side="left")

        return card

    # ------------------------------------------------------------------
    # Add contact form
    # ------------------------------------------------------------------

    def _open_add_form(self):
        self._open_contact_form("New Contact", None)

    def _open_edit_form(self, row):
        self._open_contact_form("Edit Contact", row)

    def _open_contact_form(self, title: str, row):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("440x380")
        win.minsize(400, 340)
        win.configure(bg=self.colors["bg"])
        win.transient(self.root)
        win.grab_set()

        tk.Label(win, text=title, bg=self.colors["bg"], fg=self.colors["text"],
                 font=("Arial", 13, "bold")).pack(anchor="w", padx=16, pady=(14, 8))

        form = tk.Frame(win, bg=self.colors["bg"])
        form.pack(fill="both", expand=True, padx=16)

        entries = {}
        fields = [
            ("Name *",   "name"),
            ("Company",  "company"),
            ("Phone",    "phone"),
            ("Email",    "email"),
            ("Address",  "address"),
        ]
        for label, key in fields:
            row_frame = tk.Frame(form, bg=self.colors["bg"])
            row_frame.pack(fill="x", pady=5)
            tk.Label(row_frame, text=label, bg=self.colors["bg"],
                     fg=self.colors["muted"], width=12, anchor="w").pack(side="left")
            entry = ttk.Entry(row_frame)
            entry.pack(side="left", fill="x", expand=True)
            entries[key] = entry

        # Prefill if editing
        if row:
            entries["name"].insert(0,    row[1] or "")
            entries["address"].insert(0, row[2] or "")
            entries["phone"].insert(0,   row[3] or "")
            entries["email"].insert(0,   row[4] or "")
            entries["company"].insert(0, row[5] or "")

        def save():
            name = entries["name"].get().strip()
            if not name:
                messagebox.showerror("Contact", "Name is required", parent=win)
                return
            kwargs = dict(
                name    = name,
                address = entries["address"].get().strip(),
                phone   = entries["phone"].get().strip(),
                email   = entries["email"].get().strip(),
                company = entries["company"].get().strip(),
            )
            if row:
                self.app.visitor_service.update_visitor(row[0], **kwargs)
                self.app.activity_service.log(
                    self.app.current_user, "Update Contact", f"Updated: {name}")
            else:
                self.app.visitor_service.add_visitor(**kwargs)
                self.app.activity_service.log(
                    self.app.current_user, "Add Contact", f"Added: {name}")
            win.destroy()
            self.refresh()

        btn_row = tk.Frame(win, bg=self.colors["bg"])
        btn_row.pack(fill="x", padx=16, pady=14)
        ttk.Button(btn_row, text="Save",   style="Success.TButton", command=save).pack(side="left")
        ttk.Button(btn_row, text="Cancel", style="Info.TButton",
                   command=win.destroy).pack(side="left", padx=8)

        entries["name"].focus()

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    def _delete_contact(self, visitor_id: int, name: str):
        if not messagebox.askyesno(
            "Delete Contact",
            f"Permanently delete '{name}'?",
            icon="warning",
        ):
            return
        self.app.visitor_service.delete_visitor(visitor_id)
        self.app.activity_service.log(
            self.app.current_user, "Delete Contact", f"Deleted: {name}")
        self.refresh()
