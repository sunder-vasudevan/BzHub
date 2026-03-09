"""Settings tab — company info and email configuration."""
import tkinter as tk
from tkinter import ttk, messagebox

from .base_tab import BaseTab


class SettingsTab(BaseTab):
    """Admin-only settings: company profile and SMTP email config."""

    def __init__(self, notebook: ttk.Notebook, app):
        super().__init__(notebook, app)
        self._build()

    # ------------------------------------------------------------------
    # Build UI
    # ------------------------------------------------------------------

    def _build(self):
        self.notebook.add(self.frame, text="⚙️ Settings")

        container = tk.Frame(self.frame, bg=self.colors["bg"])
        container.pack(fill="both", expand=True, padx=12, pady=12)

        header = tk.Frame(container, bg=self.colors["bg"])
        header.pack(fill="x", pady=(0, 12))
        ttk.Label(header, text="⚙️ Settings", style="Header.TLabel").pack(side="left")
        ttk.Label(header, text="Company & Email configuration",
                  style="Subheader.TLabel").pack(side="left", padx=10)

        body = tk.Frame(container, bg=self.colors["bg"])
        body.pack(fill="both", expand=True)

        # --- Company Info card ---
        company_card = tk.Frame(body, bg=self.colors["card"], padx=12, pady=12)
        company_card.pack(side="left", fill="both", expand=True, padx=(0, 8))

        title_row = tk.Frame(company_card, bg=self.colors["card"])
        title_row.pack(fill="x")
        tk.Label(title_row, text="Company Info", bg=self.colors["card"],
                 fg=self.colors["text"], font=("Arial", 10, "bold")).pack(side="left")
        self._lock_label = tk.Label(title_row, text="",
                                    bg=self.colors["card"], fg=self.colors["muted"],
                                    font=("Arial", 9))
        self._lock_label.pack(side="right")

        def co_field(label):
            return self._make_field_row(company_card, label)

        self._co_name    = co_field("Name")
        self._co_address = co_field("Address")
        self._co_phone   = co_field("Phone")
        self._co_email   = co_field("Email")
        self._co_tax     = co_field("Tax ID")
        self._co_bank    = co_field("Bank Details")

        co_btns = tk.Frame(company_card, bg=self.colors["card"])
        co_btns.pack(fill="x", pady=(8, 0))
        ttk.Button(co_btns, text="Save",   style="Success.TButton",
                   command=self._save_company).pack(side="left")
        ttk.Button(co_btns, text="Unlock", style="Info.TButton",
                   command=self._unlock_company).pack(side="left", padx=6)

        # --- Email Settings card ---
        email_card = tk.Frame(body, bg=self.colors["card"], padx=12, pady=12)
        email_card.pack(side="left", fill="both", expand=True, padx=(8, 0))

        tk.Label(email_card, text="Email Settings", bg=self.colors["card"],
                 fg=self.colors["text"], font=("Arial", 10, "bold")).pack(anchor="w")

        def em_field(label, show=None):
            row = tk.Frame(email_card, bg=self.colors["card"])
            row.pack(fill="x", pady=4)
            tk.Label(row, text=label, bg=self.colors["card"], fg=self.colors["muted"],
                     width=14, anchor="w").pack(side="left")
            entry = ttk.Entry(row, show=show) if show else ttk.Entry(row)
            entry.pack(side="left", fill="x", expand=True)
            return entry

        self._smtp_server   = em_field("SMTP Server")
        self._smtp_port     = em_field("SMTP Port")
        self._sender_email  = em_field("Sender Email")
        self._sender_pass   = em_field("Password", show="*")
        self._recipient     = em_field("Recipient")

        em_btns = tk.Frame(email_card, bg=self.colors["card"])
        em_btns.pack(fill="x", pady=(8, 0))
        ttk.Button(em_btns, text="Save", style="Success.TButton",
                   command=self._save_email).pack(side="left")
        ttk.Button(em_btns, text="Test", style="Info.TButton",
                   command=self._test_email).pack(side="left", padx=6)

        self._load_company()
        self._load_email()

    # ------------------------------------------------------------------
    # Company info helpers
    # ------------------------------------------------------------------

    @property
    def _co_entries(self):
        return [self._co_name, self._co_address, self._co_phone,
                self._co_email, self._co_tax, self._co_bank]

    def _set_company_state(self, state: str):
        for entry in self._co_entries:
            entry.configure(state=state)

    def _load_company(self):
        info = self.app.company_service.get_info()
        if info:
            for entry, key in [
                (self._co_name,    "company_name"),
                (self._co_address, "address"),
                (self._co_phone,   "phone"),
                (self._co_email,   "email"),
                (self._co_tax,     "tax_id"),
                (self._co_bank,    "bank_details"),
            ]:
                entry.delete(0, tk.END)
                entry.insert(0, info.get(key, ""))
            self._set_company_state("disabled")
            self._lock_label.config(text="Locked")
        else:
            self._set_company_state("normal")
            self._lock_label.config(text="Unlocked")

    def _save_company(self):
        name = self._co_name.get().strip()
        if not name:
            messagebox.showerror("Company Info", "Company name is required")
            return
        self.app.company_service.save_info(
            name,
            self._co_address.get().strip(),
            self._co_phone.get().strip(),
            self._co_email.get().strip(),
            self._co_tax.get().strip(),
            self._co_bank.get().strip(),
        )
        self.app.activity_service.log(
            self.app.current_user, "Company Info", "Company info updated")
        self._set_company_state("disabled")
        self._lock_label.config(text="Locked")
        messagebox.showinfo("Company Info", "Company info saved and locked")

    def _unlock_company(self):
        if messagebox.askyesno("Unlock", "Allow editing of Company Info?"):
            self._set_company_state("normal")
            self._lock_label.config(text="Unlocked")

    # ------------------------------------------------------------------
    # Email config helpers
    # ------------------------------------------------------------------

    def _load_email(self):
        cfg = self.app.email_service.get_config()
        if not cfg:
            return
        for entry, key in [
            (self._smtp_server,  "smtp_server"),
            (self._smtp_port,    "smtp_port"),
            (self._sender_email, "sender_email"),
            (self._sender_pass,  "sender_password"),
            (self._recipient,    "recipient_email"),
        ]:
            entry.delete(0, tk.END)
            entry.insert(0, str(cfg.get(key, "")))

    def _save_email(self):
        server    = self._smtp_server.get().strip()
        port_str  = self._smtp_port.get().strip()
        sender    = self._sender_email.get().strip()
        password  = self._sender_pass.get().strip()
        recipient = self._recipient.get().strip()

        if not all([server, port_str, sender, password, recipient]):
            messagebox.showerror("Email Settings", "All fields are required")
            return
        try:
            port = int(port_str)
        except ValueError:
            messagebox.showerror("Email Settings", "SMTP port must be a number")
            return

        self.app.email_service.save_config(server, port, sender, password, recipient)
        self.app.activity_service.log(
            self.app.current_user, "Email Config", "Email settings updated")
        messagebox.showinfo("Email Settings", "Email settings saved")

    def _test_email(self):
        try:
            self.app.email_service.send_email(
                "BizHub Test", "This is a test email from BizHub.")
            messagebox.showinfo("Email Settings", "Test email sent")
        except Exception as e:
            messagebox.showerror("Email Settings", f"Test email failed: {e}")
