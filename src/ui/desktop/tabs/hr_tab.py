"""HR tab — employees, payroll, appraisals, and 360 feedback."""
import tkinter as tk
from tkinter import ttk, messagebox

from src.core import CurrencyFormatter, HRCalculator
from .base_tab import BaseTab


class HRTab(BaseTab):
    """Admin HR module with four sub-tabs: Employees, Payroll, Appraisals, Feedback."""

    def __init__(self, notebook: ttk.Notebook, app):
        super().__init__(notebook, app)
        self.hr_notebook: ttk.Notebook | None = None
        self.hr_tab_index: dict = {}
        self._build()

    # ------------------------------------------------------------------
    # Build UI
    # ------------------------------------------------------------------

    def _build(self):
        self.notebook.add(self.frame, text="👔 HR")

        container = tk.Frame(self.frame, bg=self.colors["bg"])
        container.pack(fill="both", expand=True, padx=12, pady=12)

        self.hr_notebook = ttk.Notebook(container)
        self.hr_notebook.pack(fill="both", expand=True)

        emp_tab       = ttk.Frame(self.hr_notebook)
        payroll_tab   = ttk.Frame(self.hr_notebook)
        appraisal_tab = ttk.Frame(self.hr_notebook)
        feedback_tab  = ttk.Frame(self.hr_notebook)

        self.hr_notebook.add(emp_tab,       text="Employees")
        self.hr_notebook.add(payroll_tab,   text="Payroll")
        self.hr_notebook.add(appraisal_tab, text="Appraisals")
        self.hr_notebook.add(feedback_tab,  text="Feedback")

        self.hr_tab_index = {
            "Employees":  emp_tab,
            "Payroll":    payroll_tab,
            "Appraisals": appraisal_tab,
            "Feedback":   feedback_tab,
        }

        self._build_employees_ui(emp_tab)
        self._build_payroll_ui(payroll_tab)
        self._build_appraisals_ui(appraisal_tab)
        self._build_feedback_ui(feedback_tab)

    # ==================================================================
    # EMPLOYEES tab
    # ==================================================================

    def _build_employees_ui(self, parent):
        container = tk.Frame(parent, bg=self.colors["bg"])
        container.pack(fill="both", expand=True, padx=12, pady=12)

        header = tk.Frame(container, bg=self.colors["bg"])
        header.pack(fill="x", pady=(0, 12))
        ttk.Label(header, text="👔 HR", style="Header.TLabel").pack(side="left")
        ttk.Label(header, text="Employee profiles",
                  style="Subheader.TLabel").pack(side="left", padx=10)

        actions = tk.Frame(header, bg=self.colors["bg"])
        actions.pack(side="right")
        ttk.Button(actions, text="Add Employee", style="Primary.TButton",
                   command=self._open_add_employee).pack(side="left", padx=(0, 6))
        ttk.Button(actions, text="Payroll", style="Info.TButton",
                   command=lambda: self.hr_notebook.select(
                       self.hr_tab_index["Payroll"]
                   )).pack(side="left", padx=(0, 6))

        self._hr_search_var = tk.StringVar()
        ttk.Entry(actions, textvariable=self._hr_search_var, width=24).pack(side="left", padx=(0, 6))
        ttk.Button(actions, text="Search", style="Info.TButton",
                   command=self.refresh).pack(side="left", padx=4)
        ttk.Button(actions, text="Reset", style="Info.TButton",
                   command=self._reset_search).pack(side="left")

        canvas_frame = tk.Frame(container, bg=self.colors["bg"])
        canvas_frame.pack(fill="both", expand=True)

        self._hr_canvas, self._hr_scroll, self._hr_cards_frame, self._hr_window = \
            self._make_scrollable_canvas(canvas_frame)

        self.refresh()

    def _reset_search(self):
        self._hr_search_var.set("")
        self.refresh()

    def refresh(self):
        if not hasattr(self, "_hr_cards_frame"):
            return
        for w in self._hr_cards_frame.winfo_children():
            w.destroy()

        query = (self._hr_search_var.get() or "").strip().lower()
        employees = self.app.hr_service.get_all_employees()

        filtered = [
            r for r in employees
            if not query or any(
                query in str(v).lower()
                for v in [r[1] or "", r[2] or "", r[4] or "", r[6] or "", r[7] or ""]
            )
        ]

        if not filtered:
            empty = tk.Frame(self._hr_cards_frame, bg=self.colors["card"], padx=12, pady=12)
            empty.pack(fill="x", pady=6)
            tk.Label(empty, text="No employees found",
                     bg=self.colors["card"], fg=self.colors["muted"]).pack(anchor="w")
            return

        for idx, row in enumerate(filtered):
            card = self._employee_card(self._hr_cards_frame, row)
            card.grid(row=idx // 2, column=idx % 2, padx=6, pady=6, sticky="nsew")

        self._hr_cards_frame.grid_columnconfigure(0, weight=1)
        self._hr_cards_frame.grid_columnconfigure(1, weight=1)

    def _employee_card(self, parent, row) -> tk.Frame:
        emp_id       = row[0]
        emp_number   = row[1] or "—"
        name         = row[2] or "—"
        joining_date = row[3] or "—"
        designation  = row[4] or "—"
        manager      = row[5] or "—"
        team         = row[6] or "—"
        email        = row[7] or "—"
        phone        = row[8] or "—"
        is_active    = row[12] if len(row) > 12 else 1

        card = tk.Frame(parent, bg=self.colors["card"], padx=12, pady=12)

        title = tk.Frame(card, bg=self.colors["card"])
        title.pack(fill="x")
        tk.Label(title, text=name, bg=self.colors["card"], fg=self.colors["text"],
                 font=("Arial", 11, "bold")).pack(side="left")
        status_color = self.colors["accent"] if is_active else self.colors["muted"]
        tk.Label(title, text="Active" if is_active else "Inactive",
                 bg=self.colors["card"], fg=status_color,
                 font=("Arial", 9, "bold")).pack(side="right")
        tk.Label(title, text=emp_number, bg=self.colors["card"], fg=self.colors["muted"],
                 font=("Arial", 9)).pack(side="right", padx=(0, 8))

        tk.Label(card, text=designation, bg=self.colors["card"], fg=self.colors["muted"],
                 font=("Arial", 9)).pack(anchor="w", pady=(4, 0))

        info = tk.Frame(card, bg=self.colors["card"])
        info.pack(fill="x", pady=(8, 0))
        for line in [f"Team: {team}", f"Manager: {manager}", f"Joined: {joining_date}"]:
            tk.Label(info, text=line, bg=self.colors["card"], fg=self.colors["text"],
                     font=("Arial", 9)).pack(anchor="w")

        contact = tk.Frame(card, bg=self.colors["card"])
        contact.pack(fill="x", pady=(8, 0))
        tk.Label(contact, text=f"Email: {email}", bg=self.colors["card"],
                 fg=self.colors["text"], font=("Arial", 9)).pack(anchor="w")
        tk.Label(contact, text=f"Phone: {phone}", bg=self.colors["card"],
                 fg=self.colors["text"], font=("Arial", 9)).pack(anchor="w")

        btns = tk.Frame(card, bg=self.colors["card"])
        btns.pack(fill="x", pady=(10, 0))
        ttk.Button(btns, text="Print ID Card", style="Info.TButton",
                   command=lambda r=row: self._print_id_card(r)).pack(side="left")
        if is_active:
            ttk.Button(btns, text="Deactivate", style="Danger.TButton",
                       command=lambda e=emp_id: self._set_active(e, False)).pack(side="left", padx=6)
        else:
            ttk.Button(btns, text="Activate", style="Success.TButton",
                       command=lambda e=emp_id: self._set_active(e, True)).pack(side="left", padx=6)

        return card

    def _set_active(self, emp_id: int, active: bool):
        try:
            if not active:
                messagebox.showwarning("Caution", "This will deactivate the employee.")
                if not messagebox.askyesno("Confirm", "Deactivate this employee?"):
                    return
            if self.app.hr_service.update_employee(emp_id, is_active=1 if active else 0):
                self.app.activity_service.log(
                    self.app.current_user, "HR Status",
                    f"Employee {emp_id} set to {'active' if active else 'inactive'}",
                )
                self.refresh()
            else:
                messagebox.showerror("HR", "Failed to update employee status")
        except Exception as e:
            messagebox.showerror("HR", f"Failed to update status: {e}")

    def _open_add_employee(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Employee")
        dialog.geometry("460x560")
        dialog.minsize(420, 520)

        container = tk.Frame(dialog, bg=self.colors["bg"], padx=12, pady=12)
        container.pack(fill="both", expand=True)
        tk.Label(container, text="Add Employee", bg=self.colors["bg"],
                 fg=self.colors["text"], font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 8))

        fields = {}
        for label in ["Emp Number", "Name", "Joining Date", "Designation",
                      "Manager", "Team", "Email", "Phone", "Emergency", "Notes"]:
            fields[label] = self._make_field_row(container, label, bg=self.colors["bg"])

        def save():
            try:
                if self.app.hr_service.add_employee(
                    fields["Emp Number"].get().strip(),
                    fields["Name"].get().strip(),
                    fields["Joining Date"].get().strip(),
                    fields["Designation"].get().strip(),
                    fields["Manager"].get().strip(),
                    fields["Team"].get().strip(),
                    fields["Email"].get().strip(),
                    fields["Phone"].get().strip(),
                    fields["Emergency"].get().strip(),
                    "",
                    fields["Notes"].get().strip(),
                    1,
                ):
                    self.app.activity_service.log(
                        self.app.current_user, "Add Employee",
                        f"Added employee: {fields['Name'].get().strip()}",
                    )
                    self.refresh()
                    dialog.destroy()
                else:
                    messagebox.showerror("HR", "Failed to add employee")
            except Exception as e:
                messagebox.showerror("HR", f"Invalid input: {e}")

        btn_row = tk.Frame(container, bg=self.colors["bg"])
        btn_row.pack(fill="x", pady=(10, 0))
        ttk.Button(btn_row, text="Save",   style="Success.TButton", command=save).pack(side="left")
        ttk.Button(btn_row, text="Cancel", style="Info.TButton",    command=dialog.destroy).pack(side="right")

    def _print_id_card(self, row):
        emp_id       = row[0]
        emp_number   = row[1] or "—"
        name         = row[2] or "—"
        joining_date = row[3] or ""
        designation  = row[4] or "—"
        manager      = row[5] or "—"
        team         = row[6] or "—"
        email        = row[7] or "—"
        phone        = row[8] or "—"
        emergency    = row[9] or "—"

        expiry = HRCalculator.calculate_id_card_expiry(joining_date) if joining_date else ""
        info   = self.app.company_service.get_info() or {}
        company = info.get("company_name") or "BzHub"

        lines = [
            company,
            "Employee ID Card",
            "=" * 40,
            f"Employee ID:  {emp_number}",
            f"Name:         {name}",
            f"Designation:  {designation}",
            f"Team:         {team}",
            f"Manager:      {manager}",
            f"Email:        {email}",
            f"Phone:        {phone}",
            f"Emergency:    {emergency}",
        ]
        if joining_date:
            lines.append(f"Joined:       {joining_date}")
        if expiry:
            lines.append(f"Expires:      {expiry}")
        lines += ["=" * 40, f"Record ID: {emp_id}"]

        self._show_print_preview("\n".join(lines), f"Employee ID Card - {emp_number}")

    # ==================================================================
    # PAYROLL tab
    # ==================================================================

    def _build_payroll_ui(self, parent):
        container = tk.Frame(parent, bg=self.colors["bg"], padx=12, pady=12)
        container.pack(fill="both", expand=True)

        header = tk.Frame(container, bg=self.colors["bg"])
        header.pack(fill="x", pady=(0, 8))
        tk.Label(header, text="Payroll", bg=self.colors["bg"], fg=self.colors["text"],
                 font=("Arial", 12, "bold")).pack(side="left")

        body = tk.Frame(container, bg=self.colors["bg"])
        body.pack(fill="both", expand=True)

        form_card = tk.Frame(body, bg=self.colors["card"], padx=12, pady=12)
        form_card.pack(side="left", fill="y", padx=(0, 10))

        list_card = tk.Frame(body, bg=self.colors["card"], padx=12, pady=12)
        list_card.pack(side="left", fill="both", expand=True)

        def ff(label):
            return self._make_field_row(form_card, label)

        employees   = self.app.hr_service.get_all_employees()
        active_emps = [e for e in employees if len(e) > 12 and e[12] == 1]
        emp_options = [f"{e[0]} - {e[2]}" for e in active_emps]

        emp_row = tk.Frame(form_card, bg=self.colors["card"])
        emp_row.pack(fill="x", pady=4)
        tk.Label(emp_row, text="Employee", bg=self.colors["card"],
                 fg=self.colors["muted"], width=14, anchor="w").pack(side="left")
        emp_var   = tk.StringVar()
        emp_combo = ttk.Combobox(emp_row, values=emp_options,
                                 textvariable=emp_var, state="readonly")
        emp_combo.pack(side="left", fill="x", expand=True)

        period_start  = ff("Period Start")
        period_end    = ff("Period End")
        base_salary   = ff("Base Salary")
        allowances    = ff("Allowances")
        deductions    = ff("Deductions")
        overtime_hrs  = ff("Overtime Hours")
        overtime_rate = ff("Overtime Rate")
        status        = ff("Status")
        paid_date     = ff("Paid Date")
        status.insert(0, "Draft")

        cols = ("ID", "Employee", "Period", "Gross", "Net", "Status", "Paid")
        tree = ttk.Treeview(list_card, columns=cols, show="headings", height=14)
        for col, w in [("ID", 60), ("Employee", 180), ("Period", 160),
                       ("Gross", 90), ("Net", 90), ("Status", 90), ("Paid", 120)]:
            tree.column(col, anchor="center", width=w)
            tree.heading(col, text=col)
        tree.pack(fill="both", expand=True)

        emp_lookup = {e[0]: e[2] for e in employees}

        def parse_emp_id():
            if not emp_var.get():
                return None
            return int(emp_var.get().split(" - ", 1)[0])

        def refresh_list():
            for row in tree.get_children():
                tree.delete(row)
            for r in self.app.payroll_service.get_all_payrolls():
                tree.insert("", "end", values=(
                    r[0],
                    emp_lookup.get(r[1], str(r[1])),
                    f"{r[2]} → {r[3]}",
                    CurrencyFormatter.format_currency(r[9]),
                    CurrencyFormatter.format_currency(r[10]),
                    r[11],
                    r[12] or "",
                ))

        def clear_form():
            emp_var.set("")
            for e in [period_start, period_end, base_salary, allowances, deductions,
                      overtime_hrs, overtime_rate, status, paid_date]:
                e.delete(0, tk.END)
            status.insert(0, "Draft")

        def add_payroll():
            try:
                eid = parse_emp_id()
                if not eid:
                    messagebox.showerror("Payroll", "Select an employee")
                    return
                ok = self.app.payroll_service.add_payroll(
                    eid,
                    period_start.get().strip(), period_end.get().strip(),
                    float(base_salary.get() or 0), float(allowances.get() or 0),
                    float(deductions.get() or 0), float(overtime_hrs.get() or 0),
                    float(overtime_rate.get() or 0),
                    status.get().strip() or "Draft", paid_date.get().strip(),
                )
                if ok:
                    refresh_list()
                    clear_form()
                else:
                    messagebox.showerror("Payroll", "Failed to add payroll")
            except Exception as e:
                messagebox.showerror("Payroll", f"Invalid input: {e}")

        def update_payroll():
            sel = tree.selection()
            if not sel:
                messagebox.showerror("Payroll", "Select a record")
                return
            pid = tree.item(sel[0])["values"][0]
            try:
                self.app.payroll_service.update_payroll(
                    int(pid), employee_id=parse_emp_id(),
                    period_start=period_start.get().strip(),
                    period_end=period_end.get().strip(),
                    base_salary=float(base_salary.get() or 0),
                    allowances=float(allowances.get() or 0),
                    deductions=float(deductions.get() or 0),
                    overtime_hours=float(overtime_hrs.get() or 0),
                    overtime_rate=float(overtime_rate.get() or 0),
                    status=status.get().strip() or "Draft",
                    paid_date=paid_date.get().strip(),
                )
                refresh_list()
            except Exception as e:
                messagebox.showerror("Payroll", f"Invalid input: {e}")

        def delete_payroll():
            sel = tree.selection()
            if not sel:
                messagebox.showerror("Payroll", "Select a record")
                return
            pid = tree.item(sel[0])["values"][0]
            messagebox.showwarning("Caution", "This will permanently delete the payroll record.")
            if not messagebox.askyesno("Confirm", "Delete the selected payroll record?"):
                return
            if self.app.payroll_service.delete_payroll(int(pid)):
                refresh_list()
            else:
                messagebox.showerror("Payroll", "Failed to delete payroll")

        def on_select(event=None):
            sel = tree.selection()
            if not sel:
                return
            pid = tree.item(sel[0])["values"][0]
            record = next(
                (r for r in self.app.payroll_service.get_all_payrolls() if r[0] == pid), None
            )
            if not record:
                return
            emp_var.set(f"{record[1]} - {emp_lookup.get(record[1], record[1])}")
            for entry, val in [
                (period_start,  record[2]  or ""),
                (period_end,    record[3]  or ""),
                (base_salary,   str(record[4]) if record[4] is not None else "0"),
                (allowances,    str(record[5]) if record[5] is not None else "0"),
                (deductions,    str(record[6]) if record[6] is not None else "0"),
                (overtime_hrs,  str(record[7]) if record[7] is not None else "0"),
                (overtime_rate, str(record[8]) if record[8] is not None else "0"),
                (status,        record[11] or "Draft"),
                (paid_date,     record[12] or ""),
            ]:
                entry.delete(0, tk.END)
                entry.insert(0, val)

        tree.bind("<Double-1>", on_select)

        btn_row = tk.Frame(form_card, bg=self.colors["card"])
        btn_row.pack(fill="x", pady=(10, 0))
        ttk.Button(btn_row, text="Add",    style="Success.TButton", command=add_payroll).pack(side="left", padx=3)
        ttk.Button(btn_row, text="Update", style="Primary.TButton", command=update_payroll).pack(side="left", padx=3)
        ttk.Button(btn_row, text="Delete", style="Danger.TButton",  command=delete_payroll).pack(side="left", padx=3)
        ttk.Button(btn_row, text="Clear",  style="Info.TButton",    command=clear_form).pack(side="left", padx=3)

        refresh_list()

    # ==================================================================
    # APPRAISALS tab
    # ==================================================================

    def _build_appraisals_ui(self, parent):
        container = tk.Frame(parent, bg=self.colors["bg"], padx=12, pady=12)
        container.pack(fill="both", expand=True)
        tk.Label(container, text="Appraisals", bg=self.colors["bg"], fg=self.colors["text"],
                 font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 8))

        body = tk.Frame(container, bg=self.colors["bg"])
        body.pack(fill="both", expand=True)

        form_card = tk.Frame(body, bg=self.colors["card"], padx=12, pady=12)
        form_card.pack(side="left", fill="y", padx=(0, 10))

        list_card = tk.Frame(body, bg=self.colors["card"], padx=12, pady=12)
        list_card.pack(side="left", fill="both", expand=True)

        employees = self.app.hr_service.get_all_employees()
        emp_opts  = [f"{e[0]} - {e[2]}" for e in employees]
        emp_var   = tk.StringVar()

        emp_row = tk.Frame(form_card, bg=self.colors["card"])
        emp_row.pack(fill="x", pady=4)
        tk.Label(emp_row, text="Employee", bg=self.colors["card"],
                 fg=self.colors["muted"], width=14, anchor="w").pack(side="left")
        ttk.Combobox(emp_row, values=emp_opts, textvariable=emp_var,
                     state="readonly").pack(side="left", fill="x", expand=True)

        period_start  = self._make_field_row(form_card, "Period Start")
        period_end    = self._make_field_row(form_card, "Period End")

        tk.Label(form_card, text="Self Appraisal",
                 bg=self.colors["card"], fg=self.colors["muted"]).pack(anchor="w", pady=(8, 0))
        self_text = tk.Text(form_card, height=4)
        self_text.pack(fill="x", pady=(2, 6))
        self_rating = self._make_field_row(form_card, "Self Rating")

        tk.Label(form_card, text="Manager Review",
                 bg=self.colors["card"], fg=self.colors["muted"]).pack(anchor="w", pady=(8, 0))
        mgr_text = tk.Text(form_card, height=4)
        mgr_text.pack(fill="x", pady=(2, 6))
        mgr_rating   = self._make_field_row(form_card, "Manager Rating")
        final_rating = self._make_field_row(form_card, "Final Rating")

        cols = ("ID", "Employee", "Period", "Status", "Final")
        tree = ttk.Treeview(list_card, columns=cols, show="headings", height=14)
        for col, w in [("ID", 60), ("Employee", 180), ("Period", 160),
                       ("Status", 120), ("Final", 90)]:
            tree.column(col, anchor="center", width=w)
            tree.heading(col, text=col)
        tree.pack(fill="both", expand=True)

        emp_lookup = {e[0]: e[2] for e in employees}

        def parse_eid():
            return int(emp_var.get().split(" - ", 1)[0]) if emp_var.get() else None

        def refresh_list():
            for row in tree.get_children():
                tree.delete(row)
            for r in self.app.appraisal_service.get_all_appraisals():
                tree.insert("", "end", values=(
                    r[0], emp_lookup.get(r[1], str(r[1])),
                    f"{r[2]} → {r[3]}", r[4],
                    r[9] if r[9] is not None else "",
                ))

        def clear_form():
            emp_var.set("")
            for e in [period_start, period_end, self_rating, mgr_rating, final_rating]:
                e.delete(0, tk.END)
            self_text.delete("1.0", tk.END)
            mgr_text.delete("1.0", tk.END)

        def create_appraisal():
            eid = parse_eid()
            if not eid:
                messagebox.showerror("Appraisals", "Select an employee")
                return
            if self.app.appraisal_service.create_appraisal(
                eid, period_start.get().strip(), period_end.get().strip(),
                self.app.current_user or "",
            ):
                refresh_list()
                clear_form()
            else:
                messagebox.showerror("Appraisals", "Failed to create appraisal")

        def _selected_appraisal_id():
            sel = tree.selection()
            if not sel:
                messagebox.showerror("Appraisals", "Select an appraisal")
                return None
            return int(tree.item(sel[0])["values"][0])

        def submit_self():
            aid = _selected_appraisal_id()
            if aid is None:
                return
            try:
                rating = float(self_rating.get() or 0)
            except Exception:
                rating = 0
            self.app.appraisal_service.update_self_appraisal(
                aid, self_text.get("1.0", tk.END).strip(), rating)
            refresh_list()

        def submit_manager():
            aid = _selected_appraisal_id()
            if aid is None:
                return
            try:
                rating = float(mgr_rating.get() or 0)
            except Exception:
                rating = 0
            self.app.appraisal_service.update_manager_review(
                aid, mgr_text.get("1.0", tk.END).strip(), rating)
            refresh_list()

        def finalize():
            aid = _selected_appraisal_id()
            if aid is None:
                return
            try:
                rating = float(final_rating.get() or 0)
            except Exception:
                rating = 0
            self.app.appraisal_service.finalize_appraisal(aid, rating)
            refresh_list()

        def on_select(event=None):
            sel = tree.selection()
            if not sel:
                return
            aid = int(tree.item(sel[0])["values"][0])
            r = next((x for x in self.app.appraisal_service.get_all_appraisals()
                      if x[0] == aid), None)
            if not r:
                return
            emp_var.set(f"{r[1]} - {emp_lookup.get(r[1], r[1])}")
            for entry, val in [
                (period_start, r[2] or ""), (period_end,    r[3] or ""),
                (self_rating,  r[6] or ""), (mgr_rating,    r[8] or ""),
                (final_rating, r[9] or ""),
            ]:
                entry.delete(0, tk.END)
                entry.insert(0, val)
            self_text.delete("1.0", tk.END)
            self_text.insert("1.0", r[5] or "")
            mgr_text.delete("1.0", tk.END)
            mgr_text.insert("1.0", r[7] or "")

        tree.bind("<Double-1>", on_select)

        btn_row = tk.Frame(form_card, bg=self.colors["card"])
        btn_row.pack(fill="x", pady=(10, 0))
        ttk.Button(btn_row, text="Create",         style="Success.TButton", command=create_appraisal).pack(side="left", padx=3)
        ttk.Button(btn_row, text="Self Submit",    style="Primary.TButton", command=submit_self).pack(side="left", padx=3)
        ttk.Button(btn_row, text="Manager Review", style="Info.TButton",    command=submit_manager).pack(side="left", padx=3)
        ttk.Button(btn_row, text="Finalize",       style="Danger.TButton",  command=finalize).pack(side="left", padx=3)
        ttk.Button(btn_row, text="Clear",          style="Info.TButton",    command=clear_form).pack(side="left", padx=3)

        refresh_list()

    # ==================================================================
    # 360 FEEDBACK tab
    # ==================================================================

    def _build_feedback_ui(self, parent):
        container = tk.Frame(parent, bg=self.colors["bg"], padx=12, pady=12)
        container.pack(fill="both", expand=True)
        tk.Label(container, text="360 Feedback", bg=self.colors["bg"], fg=self.colors["text"],
                 font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 8))

        body = tk.Frame(container, bg=self.colors["bg"])
        body.pack(fill="both", expand=True)

        form_card = tk.Frame(body, bg=self.colors["card"], padx=12, pady=12)
        form_card.pack(side="left", fill="y", padx=(0, 10))

        list_card = tk.Frame(body, bg=self.colors["card"], padx=12, pady=12)
        list_card.pack(side="left", fill="both", expand=True)

        employees  = self.app.hr_service.get_all_employees()
        appraisals = self.app.appraisal_service.get_all_appraisals()
        emp_opts   = [f"{e[0]} - {e[2]}" for e in employees]
        app_opts   = [f"{a[0]} - {a[1]}" for a in appraisals]
        emp_lookup = {e[0]: e[2] for e in employees}

        def parse_eid(val):
            return int(val.split(" - ", 1)[0]) if val else None

        def parse_aid(val):
            return int(val.split(" - ", 1)[0]) if val else None

        # Request feedback section
        tk.Label(form_card, text="Request Feedback", bg=self.colors["card"],
                 fg=self.colors["text"], font=("Arial", 10, "bold")).pack(anchor="w")

        req_target_var = tk.StringVar()
        req_app_var    = tk.StringVar()
        for lbl, var, opts in [
            ("Target", req_target_var, emp_opts),
            ("Appraisal", req_app_var, app_opts),
        ]:
            row = tk.Frame(form_card, bg=self.colors["card"])
            row.pack(fill="x", pady=4)
            tk.Label(row, text=lbl, bg=self.colors["card"], fg=self.colors["muted"],
                     width=14, anchor="w").pack(side="left")
            ttk.Combobox(row, values=opts, textvariable=var,
                         state="readonly").pack(side="left", fill="x", expand=True)

        tk.Label(form_card, text="Message",
                 bg=self.colors["card"], fg=self.colors["muted"]).pack(anchor="w", pady=(6, 0))
        req_msg = tk.Text(form_card, height=3)
        req_msg.pack(fill="x", pady=(2, 6))

        # Give feedback section
        tk.Label(form_card, text="Give Feedback", bg=self.colors["card"],
                 fg=self.colors["text"], font=("Arial", 10, "bold")).pack(anchor="w", pady=(8, 0))

        fb_from_var = tk.StringVar()
        fb_to_var   = tk.StringVar()
        fb_app_var  = tk.StringVar()
        for lbl, var, opts in [
            ("From", fb_from_var, emp_opts),
            ("To",   fb_to_var,   emp_opts),
            ("Appraisal", fb_app_var, app_opts),
        ]:
            row = tk.Frame(form_card, bg=self.colors["card"])
            row.pack(fill="x", pady=4)
            tk.Label(row, text=lbl, bg=self.colors["card"], fg=self.colors["muted"],
                     width=14, anchor="w").pack(side="left")
            ttk.Combobox(row, values=opts, textvariable=var,
                         state="readonly").pack(side="left", fill="x", expand=True)

        fb_rating = self._make_field_row(form_card, "Rating")
        tk.Label(form_card, text="Feedback",
                 bg=self.colors["card"], fg=self.colors["muted"]).pack(anchor="w", pady=(6, 0))
        fb_text = tk.Text(form_card, height=3)
        fb_text.pack(fill="x", pady=(2, 6))

        # List sub-tabs
        list_tabs    = ttk.Notebook(list_card)
        list_tabs.pack(fill="both", expand=True)
        req_list_tab = ttk.Frame(list_tabs)
        fb_list_tab  = ttk.Frame(list_tabs)
        list_tabs.add(req_list_tab, text="Requests")
        list_tabs.add(fb_list_tab,  text="Entries")

        req_tree = ttk.Treeview(req_list_tab,
                                columns=("ID", "Target", "Status", "Message"),
                                show="headings", height=10)
        for col, w in [("ID", 60), ("Target", 160), ("Status", 90), ("Message", 240)]:
            req_tree.column(col, anchor="center", width=w)
            req_tree.heading(col, text=col)
        req_tree.pack(fill="both", expand=True)

        fb_tree = ttk.Treeview(fb_list_tab,
                               columns=("ID", "From", "To", "Rating", "Feedback"),
                               show="headings", height=10)
        for col, w in [("ID", 60), ("From", 140), ("To", 140), ("Rating", 80), ("Feedback", 240)]:
            fb_tree.column(col, anchor="center", width=w)
            fb_tree.heading(col, text=col)
        fb_tree.pack(fill="both", expand=True)

        def refresh_requests():
            for row in req_tree.get_children():
                req_tree.delete(row)
            for r in self.app.appraisal_service.get_feedback_requests():
                req_tree.insert("", "end", values=(
                    r[0], emp_lookup.get(r[3], str(r[3])),
                    r[5], (r[4] or "")[:60],
                ))

        def refresh_entries():
            for row in fb_tree.get_children():
                fb_tree.delete(row)
            for r in self.app.appraisal_service.get_feedback_entries():
                fb_tree.insert("", "end", values=(
                    r[0],
                    emp_lookup.get(r[2], str(r[2])),
                    emp_lookup.get(r[3], str(r[3])),
                    r[4] if r[4] is not None else "",
                    (r[5] or "")[:60],
                ))

        def add_request():
            tid = parse_eid(req_target_var.get())
            if not tid:
                messagebox.showerror("Feedback", "Select target employee")
                return
            aid = parse_aid(req_app_var.get())
            if self.app.appraisal_service.create_feedback_request(
                aid, self.app.current_user or "", tid,
                req_msg.get("1.0", tk.END).strip(),
            ):
                req_msg.delete("1.0", tk.END)
                refresh_requests()
            else:
                messagebox.showerror("Feedback", "Failed to create request")

        def add_feedback():
            fid = parse_eid(fb_from_var.get())
            tid = parse_eid(fb_to_var.get())
            if not fid or not tid:
                messagebox.showerror("Feedback", "Select From and To employees")
                return
            aid = parse_aid(fb_app_var.get())
            try:
                rating = float(fb_rating.get() or 0)
            except Exception:
                rating = 0
            if self.app.appraisal_service.add_feedback_entry(
                aid, fid, tid, rating, fb_text.get("1.0", tk.END).strip()
            ):
                fb_text.delete("1.0", tk.END)
                fb_rating.delete(0, tk.END)
                refresh_entries()
            else:
                messagebox.showerror("Feedback", "Failed to add feedback")

        btn_row = tk.Frame(form_card, bg=self.colors["card"])
        btn_row.pack(fill="x", pady=(8, 0))
        ttk.Button(btn_row, text="Request",      style="Primary.TButton", command=add_request).pack(side="left", padx=3)
        ttk.Button(btn_row, text="Add Feedback", style="Success.TButton", command=add_feedback).pack(side="left", padx=3)

        refresh_requests()
        refresh_entries()
