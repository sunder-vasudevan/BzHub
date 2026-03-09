"""CRM Leads Tab — full CRM module with Contacts and Pipeline (Kanban) views."""
import tkinter as tk
from tkinter import ttk, messagebox

from .base_tab import BaseTab


class CRMLeadsTab(BaseTab):
    """
    CRM module with two sub-views:
      - Contacts: searchable table with Add/Edit/Delete
      - Pipeline: Kanban board with 6 stage columns and lead cards
    """

    def __init__(self, notebook: ttk.Notebook, app):
        super().__init__(notebook, app)
        self._build()

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def _build(self):
        self.notebook.add(self.frame, text="🎯 CRM")

        container = tk.Frame(self.frame, bg=self.colors["bg"])
        container.pack(fill="both", expand=True)

        # Inner notebook for Contacts / Pipeline
        self._inner_nb = ttk.Notebook(container)
        self._inner_nb.pack(fill="both", expand=True)

        # --- Contacts sub-tab ---
        self._contacts_frame = ttk.Frame(self._inner_nb)
        self._inner_nb.add(self._contacts_frame, text="📇 Contacts")
        self._build_contacts_tab(self._contacts_frame)

        # --- Pipeline sub-tab ---
        self._pipeline_frame = ttk.Frame(self._inner_nb)
        self._inner_nb.add(self._pipeline_frame, text="📊 Pipeline")
        self._build_pipeline_tab(self._pipeline_frame)

    # ==================================================================
    # Contacts sub-tab
    # ==================================================================

    def _build_contacts_tab(self, parent):
        bg = self.colors["bg"]

        # Header row
        header = tk.Frame(parent, bg=bg)
        header.pack(fill="x", padx=12, pady=(12, 6))
        tk.Label(header, text="📇 CRM Contacts", bg=bg, fg=self.colors["text"],
                 font=("Arial", 14, "bold")).pack(side="left")

        actions = tk.Frame(header, bg=bg)
        actions.pack(side="right")
        ttk.Button(actions, text="+ Add Contact", style="Success.TButton",
                   command=self._open_add_contact).pack(side="left", padx=(0, 8))
        self._contact_search_var = tk.StringVar()
        ttk.Entry(actions, textvariable=self._contact_search_var, width=22).pack(side="left", padx=(0, 4))
        ttk.Button(actions, text="Search", style="Info.TButton",
                   command=self._refresh_contacts).pack(side="left", padx=(0, 4))
        ttk.Button(actions, text="Reset", style="Info.TButton",
                   command=self._reset_contact_search).pack(side="left")

        # Treeview
        tree_frame = tk.Frame(parent, bg=bg)
        tree_frame.pack(fill="both", expand=True, padx=12, pady=6)

        cols = ("ID", "Name", "Company", "Email", "Phone", "Source", "Status")
        self._contacts_tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=18)
        col_widths = {"ID": 40, "Name": 150, "Company": 130, "Email": 160,
                      "Phone": 110, "Source": 90, "Status": 70}
        for col in cols:
            self._contacts_tree.heading(col, text=col)
            self._contacts_tree.column(col, width=col_widths.get(col, 100), anchor="w")

        yscroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self._contacts_tree.yview)
        self._contacts_tree.configure(yscrollcommand=yscroll.set)
        self._contacts_tree.pack(side="left", fill="both", expand=True)
        yscroll.pack(side="right", fill="y")

        # Action buttons below tree
        btn_row = tk.Frame(parent, bg=bg)
        btn_row.pack(fill="x", padx=12, pady=(0, 8))
        ttk.Button(btn_row, text="Edit Selected", style="Info.TButton",
                   command=self._open_edit_contact).pack(side="left", padx=(0, 8))
        ttk.Button(btn_row, text="Delete Selected", style="Danger.TButton",
                   command=self._delete_contact).pack(side="left")

        self._refresh_contacts()

    def _refresh_contacts(self):
        search = self._contact_search_var.get().strip() or None
        contacts = self._get_crm_service().get_contacts(search=search)
        self._contacts_tree.delete(*self._contacts_tree.get_children())
        for c in contacts:
            # c: id, name, company, email, phone, source, status, notes, created_at
            self._contacts_tree.insert("", "end", iid=str(c[0]),
                                       values=(c[0], c[1], c[2], c[3], c[4], c[5], c[6]))

    def _reset_contact_search(self):
        self._contact_search_var.set("")
        self._refresh_contacts()

    def _open_add_contact(self):
        self._open_contact_dialog()

    def _open_edit_contact(self):
        sel = self._contacts_tree.selection()
        if not sel:
            messagebox.showwarning("Select Contact", "Please select a contact to edit.")
            return
        contact_id = int(sel[0])
        contacts = self._get_crm_service().get_contacts()
        contact = next((c for c in contacts if c[0] == contact_id), None)
        if contact:
            self._open_contact_dialog(contact)

    def _delete_contact(self):
        sel = self._contacts_tree.selection()
        if not sel:
            messagebox.showwarning("Select Contact", "Please select a contact to delete.")
            return
        if not messagebox.askyesno("Confirm Delete", "Delete this contact?"):
            return
        contact_id = int(sel[0])
        self._get_crm_service().delete_contact(contact_id)
        self._refresh_contacts()

    def _open_contact_dialog(self, contact=None):
        """Open Add/Edit dialog for a contact."""
        dlg = tk.Toplevel(self.root)
        dlg.title("Edit Contact" if contact else "Add Contact")
        dlg.geometry("480x400")
        dlg.grab_set()
        bg = self.colors["card"]
        dlg.configure(bg=bg)

        fields = {}
        field_defs = [
            ("Name *", "name"),
            ("Company", "company"),
            ("Email", "email"),
            ("Phone", "phone"),
            ("Source", "source"),
            ("Notes", "notes"),
        ]

        form = tk.Frame(dlg, bg=bg, padx=20, pady=20)
        form.pack(fill="both", expand=True)

        for label_text, key in field_defs:
            row = tk.Frame(form, bg=bg)
            row.pack(fill="x", pady=4)
            tk.Label(row, text=label_text, bg=bg, fg=self.colors["text"],
                     width=12, anchor="w").pack(side="left")
            if key == "notes":
                entry = tk.Text(row, height=3, width=32)
                entry.pack(side="left", fill="x", expand=True)
                if contact:
                    entry.insert("1.0", contact[7] or "")  # notes index
            else:
                entry = ttk.Entry(row, width=32)
                entry.pack(side="left", fill="x", expand=True)
                if contact:
                    idx_map = {"name": 1, "company": 2, "email": 3, "phone": 4, "source": 5}
                    val = contact[idx_map[key]] or ""
                    entry.insert(0, val)
            fields[key] = entry

        def save():
            name = fields["name"].get().strip()
            if not name:
                messagebox.showwarning("Required", "Name is required.", parent=dlg)
                return
            notes_widget = fields["notes"]
            notes = notes_widget.get("1.0", "end").strip() if isinstance(notes_widget, tk.Text) else notes_widget.get().strip()
            svc = self._get_crm_service()
            if contact:
                svc.update_contact(contact[0], name=name,
                                   company=fields["company"].get().strip(),
                                   email=fields["email"].get().strip(),
                                   phone=fields["phone"].get().strip(),
                                   source=fields["source"].get().strip(),
                                   notes=notes)
            else:
                svc.add_contact(name=name,
                                company=fields["company"].get().strip(),
                                email=fields["email"].get().strip(),
                                phone=fields["phone"].get().strip(),
                                source=fields["source"].get().strip(),
                                notes=notes)
            dlg.destroy()
            self._refresh_contacts()

        btn_row = tk.Frame(form, bg=bg)
        btn_row.pack(fill="x", pady=(12, 0))
        ttk.Button(btn_row, text="Save", style="Success.TButton", command=save).pack(side="left", padx=(0, 8))
        ttk.Button(btn_row, text="Cancel", style="Info.TButton", command=dlg.destroy).pack(side="left")

    # ==================================================================
    # Pipeline sub-tab (Kanban)
    # ==================================================================

    def _build_pipeline_tab(self, parent):
        bg = self.colors["bg"]

        header = tk.Frame(parent, bg=bg)
        header.pack(fill="x", padx=12, pady=(12, 6))
        tk.Label(header, text="📊 CRM Pipeline", bg=bg, fg=self.colors["text"],
                 font=("Arial", 14, "bold")).pack(side="left")
        ttk.Button(header, text="Refresh", style="Info.TButton",
                   command=self._refresh_pipeline).pack(side="right")

        # Stats bar
        self._stats_var = tk.StringVar(value="")
        tk.Label(header, textvariable=self._stats_var, bg=bg, fg=self.colors["muted"],
                 font=("Arial", 9)).pack(side="left", padx=12)

        # Scrollable kanban area
        kanban_outer = tk.Frame(parent, bg=bg)
        kanban_outer.pack(fill="both", expand=True, padx=12, pady=6)

        canvas = tk.Canvas(kanban_outer, bg=bg, highlightthickness=0)
        hscroll = ttk.Scrollbar(kanban_outer, orient="horizontal", command=canvas.xview)
        vscroll = ttk.Scrollbar(kanban_outer, orient="vertical", command=canvas.yview)
        canvas.configure(xscrollcommand=hscroll.set, yscrollcommand=vscroll.set)

        hscroll.pack(side="bottom", fill="x")
        vscroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self._kanban_inner = tk.Frame(canvas, bg=bg)
        self._kanban_window = canvas.create_window((0, 0), window=self._kanban_inner, anchor="nw")

        self._kanban_inner.bind("<Configure>",
                                lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfig(self._kanban_window, height=e.height))

        self._kanban_canvas = canvas
        self._refresh_pipeline()

    def _refresh_pipeline(self):
        # Clear existing columns
        for w in self._kanban_inner.winfo_children():
            w.destroy()

        svc = self._get_crm_service()
        summary = svc.get_pipeline_summary()
        conversion = svc.get_conversion_rate()
        pipeline_value = svc.get_pipeline_value()
        total_leads = sum(len(v) for v in summary.values())
        self._stats_var.set(
            f"Total: {total_leads} leads | Pipeline Value: ${pipeline_value:,.2f} | Conversion: {conversion}%"
        )

        stages = svc.STAGES
        bg = self.colors["bg"]
        card_bg = self.colors["card"]
        border = self.colors["border"]
        primary = self.colors["primary"]
        text_color = self.colors["text"]
        muted = self.colors["muted"]

        stage_colors = {
            "New": "#6366F1", "Contacted": "#0EA5E9", "Qualified": "#F59E0B",
            "Proposal": "#8B5CF6", "Won": "#10B981", "Lost": "#EF4444",
        }

        for stage in stages:
            leads = summary.get(stage, [])
            col_frame = tk.Frame(self._kanban_inner, bg=card_bg, relief="flat",
                                 bd=1, highlightbackground=border, highlightthickness=1)
            col_frame.pack(side="left", fill="y", padx=6, pady=4, anchor="n")

            # Column header
            col_color = stage_colors.get(stage, primary)
            header_frame = tk.Frame(col_frame, bg=col_color)
            header_frame.pack(fill="x")
            tk.Label(header_frame, text=f"{stage}  ({len(leads)})",
                     bg=col_color, fg="white", font=("Arial", 10, "bold"),
                     padx=10, pady=6).pack(side="left")
            ttk.Button(header_frame, text="+ Add",
                       command=lambda s=stage: self._open_add_lead_dialog(s)).pack(side="right", padx=4, pady=4)

            # Scrollable cards area within column
            col_canvas = tk.Canvas(col_frame, bg=card_bg, width=210,
                                   highlightthickness=0)
            col_vscroll = ttk.Scrollbar(col_frame, orient="vertical", command=col_canvas.yview)
            col_canvas.configure(yscrollcommand=col_vscroll.set)
            col_vscroll.pack(side="right", fill="y")
            col_canvas.pack(side="left", fill="both", expand=True)

            col_inner = tk.Frame(col_canvas, bg=card_bg)
            col_win = col_canvas.create_window((0, 0), window=col_inner, anchor="nw")
            col_inner.bind("<Configure>",
                           lambda e, c=col_canvas: c.configure(scrollregion=c.bbox("all")))
            col_canvas.bind("<Configure>",
                            lambda e, c=col_canvas, w=col_win: c.itemconfig(w, width=e.width))

            for lead in leads:
                self._build_lead_card(col_inner, lead, stage, bg=card_bg,
                                      text_color=text_color, muted=muted,
                                      border=border, primary=primary, col_color=col_color)

            # Min height placeholder when no leads
            if not leads:
                tk.Label(col_inner, text="No leads", bg=card_bg, fg=muted,
                         font=("Arial", 9, "italic"), pady=20).pack()

    def _build_lead_card(self, parent, lead, stage, bg, text_color, muted, border, primary, col_color):
        """Build a single lead card widget."""
        # lead columns: id(0), contact_id(1), title(2), stage(3), value(4),
        #               probability(5), owner(6), notes(7), created_at(8), updated_at(9), contact_name(10)
        lead_id = lead[0]
        title = lead[2] if len(lead) > 2 else "Untitled"
        value = lead[4] if len(lead) > 4 else 0
        owner = lead[6] if len(lead) > 6 else ""
        contact_name = lead[10] if len(lead) > 10 else ""

        try:
            value_fmt = f"${float(value):,.2f}"
        except (ValueError, TypeError):
            value_fmt = "$0.00"

        card = tk.Frame(parent, bg=bg, relief="flat", bd=1,
                        highlightbackground=border, highlightthickness=1)
        card.pack(fill="x", padx=6, pady=4)

        # Color accent left bar
        accent = tk.Frame(card, bg=col_color, width=4)
        accent.pack(side="left", fill="y")

        content = tk.Frame(card, bg=bg, padx=8, pady=6)
        content.pack(side="left", fill="both", expand=True)

        tk.Label(content, text=title, bg=bg, fg=text_color,
                 font=("Arial", 9, "bold"), anchor="w", wraplength=160).pack(fill="x")
        if contact_name:
            tk.Label(content, text=f"👤 {contact_name}", bg=bg, fg=muted,
                     font=("Arial", 8), anchor="w").pack(fill="x")
        tk.Label(content, text=value_fmt, bg=bg, fg=primary,
                 font=("Arial", 9, "bold"), anchor="w").pack(fill="x")
        if owner:
            tk.Label(content, text=f"Owner: {owner}", bg=bg, fg=muted,
                     font=("Arial", 8), anchor="w").pack(fill="x")

        # Action buttons
        btn_row = tk.Frame(content, bg=bg)
        btn_row.pack(fill="x", pady=(4, 0))

        ttk.Button(btn_row, text="Detail",
                   command=lambda lid=lead_id: self._open_lead_detail(lid)).pack(side="left", padx=(0, 4))

        # Move → only if not last stage
        stages = self._get_crm_service().STAGES
        if stage != stages[-1]:
            ttk.Button(btn_row, text="Move →",
                       command=lambda lid=lead_id, s=stage: self._move_lead(lid, s)).pack(side="left")

    def _move_lead(self, lead_id: int, current_stage: str):
        """Advance lead to next stage."""
        self._get_crm_service().advance_lead_stage(lead_id, current_stage)
        self._refresh_pipeline()

    def _open_add_lead_dialog(self, default_stage: str = "New"):
        """Open dialog to add a new lead."""
        svc = self._get_crm_service()
        contacts = svc.get_contacts()

        dlg = tk.Toplevel(self.root)
        dlg.title("Add Lead")
        dlg.geometry("480x420")
        dlg.grab_set()
        bg = self.colors["card"]
        dlg.configure(bg=bg)

        form = tk.Frame(dlg, bg=bg, padx=20, pady=20)
        form.pack(fill="both", expand=True)

        # Title
        tk.Label(form, text="Title *", bg=bg, fg=self.colors["text"],
                 anchor="w").pack(fill="x")
        title_entry = ttk.Entry(form, width=40)
        title_entry.pack(fill="x", pady=(0, 8))

        # Contact
        tk.Label(form, text="Contact", bg=bg, fg=self.colors["text"],
                 anchor="w").pack(fill="x")
        contact_var = tk.StringVar()
        contact_map = {}
        contact_names = ["(none)"]
        for c in contacts:
            label = f"{c[1]} ({c[2]})" if c[2] else c[1]
            contact_names.append(label)
            contact_map[label] = c[0]
        contact_cb = ttk.Combobox(form, textvariable=contact_var, values=contact_names, state="readonly", width=38)
        contact_cb.set("(none)")
        contact_cb.pack(fill="x", pady=(0, 8))

        # Stage
        tk.Label(form, text="Stage", bg=bg, fg=self.colors["text"],
                 anchor="w").pack(fill="x")
        stage_var = tk.StringVar(value=default_stage)
        stage_cb = ttk.Combobox(form, textvariable=stage_var, values=svc.STAGES, state="readonly", width=38)
        stage_cb.pack(fill="x", pady=(0, 8))

        # Value and Probability row
        vp_row = tk.Frame(form, bg=bg)
        vp_row.pack(fill="x", pady=(0, 8))
        tk.Label(vp_row, text="Value $", bg=bg, fg=self.colors["text"]).pack(side="left")
        value_entry = ttk.Entry(vp_row, width=14)
        value_entry.insert(0, "0")
        value_entry.pack(side="left", padx=(4, 16))
        tk.Label(vp_row, text="Prob %", bg=bg, fg=self.colors["text"]).pack(side="left")
        prob_entry = ttk.Entry(vp_row, width=8)
        prob_entry.insert(0, "0")
        prob_entry.pack(side="left", padx=4)

        # Owner
        tk.Label(form, text="Owner", bg=bg, fg=self.colors["text"],
                 anchor="w").pack(fill="x")
        owner_entry = ttk.Entry(form, width=40)
        owner_entry.pack(fill="x", pady=(0, 8))

        # Notes
        tk.Label(form, text="Notes", bg=bg, fg=self.colors["text"],
                 anchor="w").pack(fill="x")
        notes_text = tk.Text(form, height=3, width=40)
        notes_text.pack(fill="x", pady=(0, 8))

        def save():
            title = title_entry.get().strip()
            if not title:
                messagebox.showwarning("Required", "Title is required.", parent=dlg)
                return
            selected_contact = contact_var.get()
            contact_id = contact_map.get(selected_contact, None)
            try:
                value = float(value_entry.get())
            except ValueError:
                value = 0.0
            try:
                prob = int(prob_entry.get())
            except ValueError:
                prob = 0
            notes = notes_text.get("1.0", "end").strip()
            svc.add_lead(contact_id=contact_id, title=title, stage=stage_var.get(),
                         value=value, probability=prob, owner=owner_entry.get().strip(),
                         notes=notes)
            dlg.destroy()
            self._refresh_pipeline()

        btn_row = tk.Frame(form, bg=bg)
        btn_row.pack(fill="x")
        ttk.Button(btn_row, text="Save", style="Success.TButton", command=save).pack(side="left", padx=(0, 8))
        ttk.Button(btn_row, text="Cancel", style="Info.TButton", command=dlg.destroy).pack(side="left")

    # ==================================================================
    # Lead Detail Dialog
    # ==================================================================

    def _open_lead_detail(self, lead_id: int):
        """Open a lead detail dialog with editable fields and activity log."""
        svc = self._get_crm_service()
        leads = svc.get_leads()
        lead = next((l for l in leads if l[0] == lead_id), None)
        if not lead:
            messagebox.showerror("Not Found", "Lead not found.")
            return

        contacts = svc.get_contacts()

        dlg = tk.Toplevel(self.root)
        dlg.title(f"Lead: {lead[2]}")
        dlg.geometry("620x680")
        dlg.grab_set()
        bg = self.colors["card"]
        dlg.configure(bg=bg)

        # Main scroll canvas
        main_canvas = tk.Canvas(dlg, bg=bg, highlightthickness=0)
        main_scroll = ttk.Scrollbar(dlg, orient="vertical", command=main_canvas.yview)
        main_canvas.configure(yscrollcommand=main_scroll.set)
        main_scroll.pack(side="right", fill="y")
        main_canvas.pack(side="left", fill="both", expand=True)

        content = tk.Frame(main_canvas, bg=bg, padx=20, pady=16)
        content_window = main_canvas.create_window((0, 0), window=content, anchor="nw")
        content.bind("<Configure>",
                     lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all")))
        main_canvas.bind("<Configure>",
                         lambda e: main_canvas.itemconfig(content_window, width=e.width))

        tk.Label(content, text="Lead Details", bg=bg, fg=self.colors["text"],
                 font=("Arial", 13, "bold")).pack(anchor="w", pady=(0, 12))

        # --- Editable lead fields ---
        fields_frame = tk.Frame(content, bg=bg)
        fields_frame.pack(fill="x")

        def labeled_entry(parent, label, value, row):
            tk.Label(parent, text=label, bg=bg, fg=self.colors["muted"],
                     width=12, anchor="w").grid(row=row, column=0, sticky="w", pady=3)
            entry = ttk.Entry(parent, width=36)
            entry.insert(0, str(value) if value is not None else "")
            entry.grid(row=row, column=1, sticky="ew", pady=3, padx=(8, 0))
            return entry

        title_entry = labeled_entry(fields_frame, "Title *", lead[2], 0)

        # Stage dropdown
        tk.Label(fields_frame, text="Stage", bg=bg, fg=self.colors["muted"],
                 width=12, anchor="w").grid(row=1, column=0, sticky="w", pady=3)
        stage_var = tk.StringVar(value=lead[3])
        stage_cb = ttk.Combobox(fields_frame, textvariable=stage_var, values=svc.STAGES,
                                 state="readonly", width=34)
        stage_cb.grid(row=1, column=1, sticky="ew", pady=3, padx=(8, 0))

        value_entry = labeled_entry(fields_frame, "Value $", lead[4], 2)
        prob_entry = labeled_entry(fields_frame, "Probability %", lead[5], 3)
        owner_entry = labeled_entry(fields_frame, "Owner", lead[6], 4)
        fields_frame.columnconfigure(1, weight=1)

        tk.Label(content, text="Notes", bg=bg, fg=self.colors["muted"],
                 anchor="w").pack(fill="x", pady=(8, 2))
        notes_text = tk.Text(content, height=3, width=50)
        notes_text.insert("1.0", lead[7] or "")
        notes_text.pack(fill="x")

        # --- Activities section ---
        tk.Label(content, text="Activity Log", bg=bg, fg=self.colors["text"],
                 font=("Arial", 11, "bold")).pack(anchor="w", pady=(16, 6))

        activities_frame = tk.Frame(content, bg=bg)
        activities_frame.pack(fill="x")

        def _refresh_activities():
            for w in activities_frame.winfo_children():
                w.destroy()
            activities = svc.get_activities(lead_id)
            if not activities:
                tk.Label(activities_frame, text="No activities yet.", bg=bg,
                         fg=self.colors["muted"], font=("Arial", 9, "italic")).pack(anchor="w")
                return
            for act in activities:
                # act: id(0), lead_id(1), type(2), note(3), due_date(4), done(5), created_at(6)
                act_id = act[0]
                act_type = act[2]
                act_note = act[3]
                act_due = act[4]
                act_done = act[5]
                act_date = act[6][:10] if act[6] else ""

                row_bg = "#F0FDF4" if act_done else bg
                act_row = tk.Frame(activities_frame, bg=row_bg, relief="flat", bd=0,
                                   highlightbackground=self.colors["border"], highlightthickness=1)
                act_row.pack(fill="x", pady=2)

                type_icons = {"call": "📞", "email": "📧", "meeting": "🤝", "note": "📝"}
                icon = type_icons.get(act_type, "📝")
                tk.Label(act_row, text=f"{icon} [{act_type.upper()}]", bg=row_bg,
                         fg=self.colors["muted"], font=("Arial", 8, "bold"),
                         padx=6, pady=4).pack(side="left")
                tk.Label(act_row, text=act_note, bg=row_bg, fg=self.colors["text"],
                         font=("Arial", 9), wraplength=300, justify="left").pack(side="left", fill="x", expand=True)
                if act_due:
                    tk.Label(act_row, text=f"Due: {act_due}", bg=row_bg, fg=self.colors["muted"],
                             font=("Arial", 8)).pack(side="left", padx=4)
                tk.Label(act_row, text=act_date, bg=row_bg, fg=self.colors["muted"],
                         font=("Arial", 8)).pack(side="left", padx=4)
                done_text = "✓ Done" if act_done else "Mark Done"
                if not act_done:
                    ttk.Button(act_row, text=done_text,
                               command=lambda aid=act_id: (_done_activity(aid))).pack(side="right", padx=4)

        def _done_activity(act_id):
            svc.complete_activity(act_id)
            _refresh_activities()

        _refresh_activities()

        # --- Add Activity form ---
        tk.Label(content, text="Add Activity", bg=bg, fg=self.colors["text"],
                 font=("Arial", 11, "bold")).pack(anchor="w", pady=(16, 6))

        act_form = tk.Frame(content, bg=bg)
        act_form.pack(fill="x")

        act_type_row = tk.Frame(act_form, bg=bg)
        act_type_row.pack(fill="x", pady=3)
        tk.Label(act_type_row, text="Type", bg=bg, fg=self.colors["muted"],
                 width=12, anchor="w").pack(side="left")
        act_type_var = tk.StringVar(value="note")
        act_type_cb = ttk.Combobox(act_type_row, textvariable=act_type_var,
                                    values=["call", "email", "meeting", "note"],
                                    state="readonly", width=18)
        act_type_cb.pack(side="left", padx=(8, 0))

        act_due_row = tk.Frame(act_form, bg=bg)
        act_due_row.pack(fill="x", pady=3)
        tk.Label(act_due_row, text="Due Date", bg=bg, fg=self.colors["muted"],
                 width=12, anchor="w").pack(side="left")
        act_due_entry = ttk.Entry(act_due_row, width=18)
        act_due_entry.insert(0, "YYYY-MM-DD")
        act_due_entry.pack(side="left", padx=(8, 0))

        tk.Label(act_form, text="Note", bg=bg, fg=self.colors["muted"], anchor="w").pack(fill="x", pady=(3, 2))
        act_note_text = tk.Text(act_form, height=3, width=50)
        act_note_text.pack(fill="x")

        def add_activity():
            note = act_note_text.get("1.0", "end").strip()
            due = act_due_entry.get().strip()
            if due == "YYYY-MM-DD":
                due = ""
            svc.add_activity(lead_id=lead_id, activity_type=act_type_var.get(),
                             note=note, due_date=due)
            act_note_text.delete("1.0", "end")
            _refresh_activities()

        ttk.Button(act_form, text="+ Add Activity", style="Success.TButton",
                   command=add_activity).pack(anchor="w", pady=(8, 0))

        # --- Save / Close buttons ---
        def save_lead():
            title_val = title_entry.get().strip()
            if not title_val:
                messagebox.showwarning("Required", "Title is required.", parent=dlg)
                return
            try:
                val = float(value_entry.get())
            except ValueError:
                val = 0.0
            try:
                prob = int(prob_entry.get())
            except ValueError:
                prob = 0
            notes_val = notes_text.get("1.0", "end").strip()
            svc.update_lead(lead_id, title=title_val, stage=stage_var.get(),
                            value=val, probability=prob, owner=owner_entry.get().strip(),
                            notes=notes_val)
            dlg.destroy()
            self._refresh_pipeline()

        btn_row = tk.Frame(content, bg=bg)
        btn_row.pack(fill="x", pady=(16, 4))
        ttk.Button(btn_row, text="Save", style="Success.TButton", command=save_lead).pack(side="left", padx=(0, 8))
        ttk.Button(btn_row, text="Delete Lead", style="Danger.TButton",
                   command=lambda: (svc.delete_lead(lead_id), dlg.destroy(), self._refresh_pipeline())).pack(side="left", padx=(0, 8))
        ttk.Button(btn_row, text="Close", style="Info.TButton", command=dlg.destroy).pack(side="left")

    # ==================================================================
    # Helpers
    # ==================================================================

    def _get_crm_service(self):
        """Return the CRMService from the app, creating it if needed."""
        return getattr(self.app, 'crm_service', None) or self._create_fallback_service()

    def _create_fallback_service(self):
        """Create a CRM service fallback using the app's DB adapter."""
        from src.services.crm_service import CRMService
        return CRMService(self.app.db)

    def refresh(self):
        """Refresh both sub-tabs."""
        self._refresh_contacts()
        self._refresh_pipeline()
