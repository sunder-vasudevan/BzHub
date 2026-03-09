"""BizHub Desktop Application — lean shell.

All tab UI and logic lives in src/ui/desktop/tabs/.
This file owns: login, theme, navigation, sidebar, help, session, quick actions.
"""
import os
import sys
import json
import logging
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont, ImageTk

# Ensure project root is in sys.path for src imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.db import SQLiteAdapter
from src.services import (
    AuthService, InventoryService, POSService, HRService,
    VisitorService, EmailService, ActivityService, CompanyService, AnalyticsService,
    PayrollService, AppraisalService,
)
from src.ui.desktop.tabs import DashboardTab, CRMTab, HRTab, SettingsTab

logger = logging.getLogger(__name__)


class BizHubDesktopApp:
    """Main BizHub desktop application using Tkinter."""

    def __init__(self, root, db_file="inventory.db"):
        logger.debug("BizHubDesktopApp.__init__ started")
        self.root = root
        self.root.title("BzHub - Complete ERP Suite")
        self.root.geometry("1200x800")

        self.dark_mode = tk.BooleanVar(value=False)

        # Services
        self.db = SQLiteAdapter(db_file)
        self.auth_service        = AuthService(self.db)
        self.inventory_service   = InventoryService(self.db)
        self.pos_service         = POSService(self.db)
        self.hr_service          = HRService(self.db)
        self.payroll_service     = PayrollService(self.db)
        self.appraisal_service   = AppraisalService(self.db)
        self.visitor_service     = VisitorService(self.db)
        self.email_service       = EmailService(self.db)
        self.activity_service    = ActivityService(self.db)
        self.company_service     = CompanyService(self.db)
        self.analytics_service   = AnalyticsService(self.db)
        logger.debug("All services initialized")

        # Session state
        self.current_user: str | None = None
        self.current_role: str | None = None
        self.colors: dict = {}

        # Feature access control
        self.feature_access = {
            "dashboard":          ["admin", "manager", "staff", "viewer"],
            "inventory":          ["admin", "manager", "staff"],
            "sales":              ["admin", "manager", "staff"],
            "reports":            ["admin", "manager"],
            "hr":                 ["admin", "manager"],
            "settings":           ["admin"],
            "feature_management": ["admin"],
        }

        # Tab/nav references (set in show_main_ui)
        self._tab_instances: dict = {}
        self._crm_tab: CRMTab | None = None
        self.pos_tab = None           # set after CRMTab is built (used by BillsTab)
        self.tab_index: dict = {}
        self.quick_actions: list = []

        # Responsive sidebar state
        self._sidebar_compact   = False
        self._topnav_compact    = False

        # Load persisted preferences, then show login
        self._load_ui_preferences()
        logger.debug("Calling show_login_screen")
        self.show_login_screen()

    # ==========================================================================
    # Theme
    # ==========================================================================

    def apply_theme(self):
        """Apply light/dark theme styles to ttk and root."""
        logger.debug("apply_theme called")
        light = {
            "bg":          "#F5F6FA",
            "card":        "#FFFFFF",
            "text":        "#111827",
            "muted":       "#6B7280",
            "primary":     "#6D28D9",
            "accent":      "#22D3EE",
            "nav_bg":      "#FFFFFF",
            "sidebar_bg":  "#F3F4F6",
            "border":      "#E5E7EB",
        }
        dark = {
            "bg":          "#0B1020",
            "card":        "#111827",
            "text":        "#F9FAFB",
            "muted":       "#9CA3AF",
            "primary":     "#8B5CF6",
            "accent":      "#22D3EE",
            "nav_bg":      "#0F172A",
            "sidebar_bg":  "#0F172A",
            "border":      "#1F2937",
        }
        self.colors = dark if self.dark_mode.get() else light

        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        self.root.configure(bg=self.colors["bg"])

        style.configure("TFrame",           background=self.colors["bg"])
        style.configure("Card.TFrame",      background=self.colors["card"])
        style.configure("TLabel",           background=self.colors["bg"],   foreground=self.colors["text"])
        style.configure("Card.TLabel",      background=self.colors["card"], foreground=self.colors["text"])
        style.configure("Header.TLabel",    background=self.colors["bg"],   foreground=self.colors["text"],
                        font=("Arial", 16, "bold"))
        style.configure("Subheader.TLabel", background=self.colors["bg"],   foreground=self.colors["muted"],
                        font=("Arial", 10))

        style.configure("Nav.TButton",     foreground=self.colors["text"], background=self.colors["nav_bg"],     padding=6)
        style.map("Nav.TButton",      background=[("active", self.colors["primary"])], foreground=[("active", "white")])

        style.configure("Sidebar.TButton", foreground=self.colors["text"], background=self.colors["sidebar_bg"], padding=6)
        style.map("Sidebar.TButton",  background=[("active", self.colors["primary"])], foreground=[("active", "white")])

        style.configure("Success.TButton", foreground="white", background=self.colors["primary"], padding=6)
        style.map("Success.TButton",  background=[("active", self.colors["accent"])])

        style.configure("Danger.TButton",  foreground="white", background="#EF4444", padding=6)
        style.map("Danger.TButton",   background=[("active", "#DC2626")])

        style.configure("Primary.TButton", foreground="white", background=self.colors["primary"], padding=6)
        style.map("Primary.TButton",  background=[("active", self.colors["accent"])])

        style.configure("Info.TButton",    foreground=self.colors["text"],  background=self.colors["card"],      padding=6)

        style.configure("Treeview",
                        background=self.colors["card"],
                        fieldbackground=self.colors["card"],
                        foreground=self.colors["text"],
                        bordercolor=self.colors["border"],
                        rowheight=24)
        style.map("Treeview",
                  background=[("selected", self.colors["primary"])],
                  foreground=[("selected", "white")])
        style.configure("Treeview.Heading", background=self.colors["bg"], foreground=self.colors["text"], relief="flat")

        style.configure("App.TNotebook", background=self.colors["bg"], borderwidth=0)
        style.layout("App.TNotebook.Tab", [])

    # ==========================================================================
    # Login
    # ==========================================================================

    def clear_root(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_login_screen(self):
        logger.debug("show_login_screen called")
        self.root.geometry("520x520")
        self.root.minsize(520, 520)
        self.root.configure(bg="#FFEE99")

        logo_img = self._load_login_logo()
        if logo_img:
            lbl = tk.Label(self.root, image=logo_img, bg="#FFEE99")
            lbl.image = logo_img
            lbl.pack(pady=(16, 4))

        tk.Label(self.root, text="BizHub Login", font=("Arial", 16, "bold"), bg="#FFEE99", fg="#222").pack(pady=(0, 8))
        tk.Label(self.root, text="Username:", bg="#FFEE99").pack()
        username_entry = tk.Entry(self.root)
        username_entry.pack(pady=5)
        tk.Label(self.root, text="Password:", bg="#FFEE99").pack()
        password_entry = tk.Entry(self.root, show="*")
        password_entry.pack(pady=5)

        def login():
            username = username_entry.get().strip()
            password = password_entry.get()
            if not username or not password:
                messagebox.showerror("Error", "Username and password required")
                return
            if self.auth_service.authenticate(username, password):
                self.current_user = username
                self.current_role = self.auth_service.get_user_role(username)
                self.auth_service.update_last_login(username)
                self.activity_service.log(username, "Login", "User logged in")
                self.root.unbind("<Return>")
                self.show_main_ui()
            else:
                messagebox.showerror("Login Failed", "Invalid credentials")

        tk.Button(self.root, text="Login", command=login,
                  bg="#6D28D9", fg="white", font=("Arial", 12, "bold")).pack(pady=10)
        tk.Button(self.root, text="Exit", command=self.root.quit, bg="#EF4444", fg="white").pack()
        self.root.bind("<Return>", lambda _e: login())
        username_entry.focus()

    # ==========================================================================
    # Main UI
    # ==========================================================================

    def show_main_ui(self):
        self._apply_responsive_geometry()
        self.clear_root()
        self.apply_theme()

        # ── Top navigation bar ─────────────────────────────────────────────
        self.top_nav = tk.Frame(self.root, bg=self.colors["nav_bg"], height=56)
        self.top_nav.pack(fill="x")

        brand_frame = tk.Frame(self.top_nav, bg=self.colors["nav_bg"])
        brand_frame.pack(side="left", padx=16)
        tk.Label(brand_frame, text="BzHub", fg=self.colors["primary"], bg=self.colors["nav_bg"],
                 font=("Arial", 14, "bold")).pack(side="left")
        tk.Label(brand_frame, text="ERP", fg=self.colors["muted"], bg=self.colors["nav_bg"],
                 font=("Arial", 10)).pack(side="left", padx=(8, 0))

        nav_frame = tk.Frame(self.top_nav, bg=self.colors["nav_bg"])
        nav_frame.pack(side="left", padx=24)

        self.nav_buttons: dict = {}
        self.nav_button_texts: dict = {}
        nav_items = [
            ("📊 Dashboard", "Dashboard", self.current_role == "admin"),
            ("📇 CRM",       "CRM",       True),
            ("👔 HR",        "HR",        self.current_role == "admin"),
            ("⚙️ Settings",  "Settings",  self.current_role == "admin"),
        ]
        for label, base_name, visible in nav_items:
            if not visible:
                continue
            btn = ttk.Button(nav_frame, text=label, style="Nav.TButton",
                             command=lambda n=base_name: self.select_tab(n))
            btn.pack(side="left", padx=4)
            self.nav_buttons[base_name]      = btn
            self.nav_button_texts[base_name] = label

        right_frame = tk.Frame(self.top_nav, bg=self.colors["nav_bg"])
        right_frame.pack(side="right", padx=16)
        self.right_frame = right_frame

        self.help_btn = ttk.Button(right_frame, text="Help", command=self.open_help, style="Info.TButton")
        self.help_btn.pack(side="left", padx=8)
        self.dark_mode_toggle = ttk.Checkbutton(right_frame, text="Dark Mode",
                                                variable=self.dark_mode,
                                                command=self.toggle_dark_mode)
        self.dark_mode_toggle.pack(side="left", padx=12)
        self.user_label = ttk.Label(right_frame, text=self.current_user, style="TLabel")
        self.user_label.pack(side="left", padx=8)
        self.logout_btn = ttk.Button(right_frame, text="Logout", command=self.logout, style="Danger.TButton")
        self.logout_btn.pack(side="left")

        # ── Main layout ────────────────────────────────────────────────────
        main_layout = tk.Frame(self.root, bg=self.colors["bg"])
        main_layout.pack(fill="both", expand=True)

        # Sidebar
        self.sidebar = tk.Frame(main_layout, bg=self.colors["sidebar_bg"], width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.sidebar_title_label = tk.Label(self.sidebar, text="Quick Actions",
                                            fg=self.colors["text"], bg=self.colors["sidebar_bg"],
                                            font=("Arial", 10, "bold"))
        self.sidebar_title_label.pack(anchor="w", padx=12, pady=(12, 8))
        self.quick_actions_container = tk.Frame(self.sidebar, bg=self.colors["sidebar_bg"])
        self.quick_actions_container.pack(fill="x")
        self.quick_actions = self._load_quick_actions()
        self.render_quick_actions()

        self.manage_actions_btn = ttk.Button(self.sidebar, text="⚙️ Manage Actions",
                                             style="Sidebar.TButton",
                                             command=self.open_quick_actions_manager)
        self.manage_actions_btn.pack(fill="x", padx=10, pady=(10, 4))

        # Content area
        content = tk.Frame(main_layout, bg=self.colors["bg"])
        content.pack(side="left", fill="both", expand=True, padx=12, pady=12)

        # Hidden-tabs notebook
        self.notebook = ttk.Notebook(content, style="App.TNotebook")
        self.notebook.pack(fill="both", expand=True)

        # ── Build tabs ─────────────────────────────────────────────────────
        self.tab_index      = {}
        self._tab_instances = {}
        self._crm_tab       = None
        self.pos_tab        = None

        if self.current_role == "admin":
            dt = DashboardTab(self.notebook, self)
            self._tab_instances["Dashboard"] = dt
            self.tab_index["Dashboard"]      = dt.frame

        crm = CRMTab(self.notebook, self)
        self._crm_tab = crm
        self.tab_index["CRM"] = crm.frame
        for name, tab in crm._sub_tabs.items():
            self._tab_instances[name] = tab
        self.pos_tab = crm.get_sub_tab("POS")

        if self.current_role == "admin":
            ht = HRTab(self.notebook, self)
            self._tab_instances["HR"] = ht
            self.tab_index["HR"]      = ht.frame

            st = SettingsTab(self.notebook, self)
            self._tab_instances["Settings"] = st
            self.tab_index["Settings"]       = st.frame

        # Default selection
        default = "Dashboard" if self.current_role == "admin" else "Inventory"
        self.select_tab(default)

        self._apply_sidebar_responsive()
        self._apply_top_nav_responsive()
        self.root.bind("<F1>",        lambda _e: self.open_help())
        self.root.bind("<Configure>", self._on_root_resize, add="+")

    # ==========================================================================
    # Tab navigation
    # ==========================================================================

    def select_tab(self, name: str):
        """Switch to a named main or sub-tab and refresh its data."""
        try:
            if name in self.tab_index:
                self.notebook.select(self.tab_index[name])
                self.notebook.update_idletasks()
            elif self._crm_tab and name in self._crm_tab.crm_tab_index:
                self.notebook.select(self.tab_index["CRM"])
                self.notebook.update_idletasks()
                self._crm_tab.select_sub_tab(name)

            # Refresh data for tabs that support it
            refreshable = {"Dashboard", "HR", "Bills", "Visitors", "Reports"}
            if name in refreshable and name in self._tab_instances:
                self._tab_instances[name].refresh()

        except Exception as e:
            import traceback
            try:
                logs_dir = os.path.abspath(
                    os.path.join(os.path.dirname(__file__), "../../../logs"))
                os.makedirs(logs_dir, exist_ok=True)
                with open(os.path.join(logs_dir, "ui_errors.log"), "a") as f:
                    f.write(f"\n=== UI Navigation Error ===\nTab: {name}\n")
                    f.write(traceback.format_exc())
            except Exception:
                pass
            messagebox.showerror("Navigation Error", f"Failed to open {name}: {e}")

    # ==========================================================================
    # Help
    # ==========================================================================

    def open_help(self):
        context = self._get_help_context()
        section  = self._get_help_section_title(context)
        text     = self._load_help_text()
        if section:
            content = self._extract_help_section(text, section)
            title   = f"Help: {section}"
        else:
            content = text
            title   = "BzHub Help"
        self._show_help_dialog(title, content)

    def _get_help_context(self) -> str:
        main_tab = self._get_selected_tab_name(self.notebook, self.tab_index)
        if main_tab == "CRM" and self._crm_tab and self._crm_tab.crm_notebook:
            sub = self._get_selected_tab_name(
                self._crm_tab.crm_notebook, self._crm_tab.crm_tab_index)
            return f"CRM/{sub}" if sub else "CRM"
        if main_tab == "HR" and "HR" in self._tab_instances:
            hr = self._tab_instances["HR"]
            if hr.hr_notebook:
                sub = self._get_selected_tab_name(hr.hr_notebook, hr.hr_tab_index)
                return f"HR/{sub}" if sub else "HR"
        return main_tab or ""

    def _get_selected_tab_name(self, notebook: ttk.Notebook, mapping: dict) -> str:
        try:
            selected = notebook.select()
            for name, frame in mapping.items():
                if str(frame) == selected:
                    return name
            tab_text = notebook.tab(selected, "text")
            return tab_text.split(" ", 1)[1] if " " in tab_text else tab_text
        except Exception:
            return ""

    def _get_help_section_title(self, context: str) -> str:
        mapping = {
            "Dashboard":      "Dashboard",
            "CRM":            "CRM",
            "CRM/Inventory":  "Inventory (CRM)",
            "CRM/POS":        "POS (CRM)",
            "CRM/Reports":    "Reports (CRM)",
            "CRM/Bills":      "Bills (CRM)",
            "CRM/Visitors":   "Visitors (CRM)",
            "HR":             "HR",
            "HR/Employees":   "Employees (HR)",
            "HR/Payroll":     "Payroll (HR)",
            "HR/Appraisals":  "Appraisals (HR)",
            "HR/Feedback":    "Feedback (HR)",
            "Settings":       "Settings",
        }
        return mapping.get(context, "")

    def _load_help_text(self) -> str:
        help_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../../documentation/HELP.md"))
        try:
            with open(help_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            return "BzHub help content is unavailable."

    def _extract_help_section(self, text: str, title: str) -> str:
        lines  = text.splitlines()
        target = title.strip().lower()
        start  = None
        level  = None
        for i, line in enumerate(lines):
            s = line.strip()
            if s.startswith("#"):
                hashes = len(s) - len(s.lstrip("#"))
                if s.strip("# ").strip().lower() == target:
                    start = i
                    level = hashes
                    break
        if start is None:
            return text
        end = len(lines)
        for j in range(start + 1, len(lines)):
            s = lines[j].strip()
            if s.startswith("#"):
                if len(s) - len(s.lstrip("#")) <= level:
                    end = j
                    break
        return "\n".join(lines[start:end]).strip()

    def _show_help_dialog(self, title: str, content: str):
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("760x560")
        dialog.configure(bg=self.colors["bg"])
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(dialog, text=title, bg=self.colors["bg"], fg=self.colors["text"],
                 font=("Arial", 12, "bold")).pack(anchor="w", padx=12, pady=(12, 6))

        body = tk.Frame(dialog, bg=self.colors["bg"])
        body.pack(fill="both", expand=True, padx=12, pady=6)
        scrollbar = ttk.Scrollbar(body, orient="vertical")
        text_w = tk.Text(body, wrap="word", yscrollcommand=scrollbar.set,
                         bg=self.colors["card"], fg=self.colors["text"],
                         insertbackground=self.colors["text"], relief="flat")
        scrollbar.config(command=text_w.yview)
        scrollbar.pack(side="right", fill="y")
        text_w.pack(side="left", fill="both", expand=True)
        text_w.insert("1.0", content)
        text_w.config(state="disabled")

        ttk.Button(dialog, text="Close", style="Info.TButton",
                   command=dialog.destroy).pack(side="right", padx=12, pady=(0, 12))

    # ==========================================================================
    # Dark mode & preferences
    # ==========================================================================

    def toggle_dark_mode(self):
        self._save_ui_preferences()
        self.apply_theme()
        self.show_main_ui()

    def _get_ui_prefs_path(self) -> str:
        assets_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../../assets"))
        os.makedirs(assets_dir, exist_ok=True)
        return os.path.join(assets_dir, "ui_preferences.json")

    def _load_ui_preferences(self):
        path = self._get_ui_prefs_path()
        if not os.path.exists(path):
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                prefs = json.load(f)
            if isinstance(prefs, dict):
                self.dark_mode.set(bool(prefs.get("dark_mode", False)))
        except Exception:
            pass

    def _save_ui_preferences(self):
        try:
            with open(self._get_ui_prefs_path(), "w", encoding="utf-8") as f:
                json.dump({
                    "dark_mode":  bool(self.dark_mode.get()),
                    "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }, f, indent=2)
        except Exception:
            pass

    # ==========================================================================
    # Logout
    # ==========================================================================

    def logout(self):
        self.activity_service.log(self.current_user, "Logout", "User logged out")
        self.current_user = None
        self.current_role = None
        self.show_login_screen()

    # ==========================================================================
    # Quick actions (sidebar)
    # ==========================================================================

    def _get_quick_actions_path(self) -> str:
        assets_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../../assets"))
        os.makedirs(assets_dir, exist_ok=True)
        return os.path.join(assets_dir, "quick_actions.json")

    def _default_quick_actions(self) -> list:
        return [
            {"label": "➕ Add Item",    "target": "Inventory"},
            {"label": "🧾 New Sale",    "target": "POS"},
            {"label": "⚠️ Low Stock",  "target": "low_stock"},
            {"label": "📈 Projections", "target": "Dashboard"},
        ]

    def _load_quick_actions(self) -> list:
        path = self._get_quick_actions_path()
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list):
                    return data
            except Exception:
                pass
        return self._default_quick_actions()

    def _save_quick_actions(self):
        try:
            with open(self._get_quick_actions_path(), "w", encoding="utf-8") as f:
                json.dump(self.quick_actions, f, indent=2)
        except Exception:
            pass

    def render_quick_actions(self):
        if not hasattr(self, "quick_actions_container"):
            return
        for w in self.quick_actions_container.winfo_children():
            w.destroy()
        for action in self.quick_actions:
            target = action.get("target")
            if target in {"Dashboard", "Reports", "HR", "Settings"} and self.current_role != "admin":
                continue
            label = action.get("label") or target
            if self._sidebar_compact:
                label = label.split(" ", 1)[0] if " " in label else label[:2]
            ttk.Button(self.quick_actions_container, text=label, style="Sidebar.TButton",
                       command=lambda t=target: self.handle_quick_action(t)).pack(fill="x", padx=10, pady=4)

    def handle_quick_action(self, target: str):
        if target == "low_stock":
            self.show_low_stock_popup()
        else:
            self.select_tab(target)

    def show_low_stock_popup(self):
        items = self.inventory_service.get_low_stock_items()
        if not items:
            messagebox.showinfo("Low Stock", "No low stock items found.")
            return
        msg = "\n".join(f"- {i[0]} (Qty: {i[1]}, Threshold: {i[2]})" for i in items[:10])
        messagebox.showinfo("Low Stock", msg)

    def open_quick_actions_manager(self):
        manager = tk.Toplevel(self.root)
        manager.title("Manage Quick Actions")
        manager.geometry("420x420")
        manager.minsize(420, 420)

        container = ttk.Frame(manager, padding=12)
        container.pack(fill="both", expand=True)
        ttk.Label(container, text="Quick Actions", style="Header.TLabel").pack(anchor="w", pady=(0, 8))

        list_frame = ttk.Frame(container)
        list_frame.pack(fill="both", expand=True)
        listbox   = tk.Listbox(list_frame, height=10)
        listbox.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=listbox.yview)
        scrollbar.pack(side="right", fill="y")
        listbox.configure(yscrollcommand=scrollbar.set)

        form = ttk.Frame(container)
        form.pack(fill="x", pady=(10, 0))
        ttk.Label(form, text="Label").grid(row=0, column=0, sticky="w")
        label_entry = ttk.Entry(form)
        label_entry.grid(row=0, column=1, sticky="ew", padx=(8, 0))

        ttk.Label(form, text="Action").grid(row=1, column=0, sticky="w", pady=(8, 0))
        action_var = tk.StringVar(value="Inventory")
        action_options = [
            "Inventory", "POS", "Bills", "Visitors", "Dashboard",
            "Reports", "HR", "Settings", "Low Stock",
        ]
        action_combo = ttk.Combobox(form, values=action_options,
                                    textvariable=action_var, state="readonly")
        action_combo.grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=(8, 0))
        form.columnconfigure(1, weight=1)

        def refresh_list():
            listbox.delete(0, tk.END)
            for a in self.quick_actions:
                lbl    = a.get("label") or a.get("target")
                tgt    = a.get("target")
                display = "Low Stock" if tgt == "low_stock" else tgt
                listbox.insert(tk.END, f"{lbl} → {display}")

        def add_action():
            lbl    = label_entry.get().strip()
            tgt_lbl = action_var.get()
            tgt    = "low_stock" if tgt_lbl == "Low Stock" else tgt_lbl
            self.quick_actions.append({"label": lbl or tgt_lbl, "target": tgt})
            self._save_quick_actions()
            self.render_quick_actions()
            refresh_list()
            label_entry.delete(0, tk.END)

        def remove_action():
            sel = listbox.curselection()
            if not sel:
                return
            idx = sel[0]
            if 0 <= idx < len(self.quick_actions):
                messagebox.showwarning("Caution", "You are about to remove a Quick Action.")
                if not messagebox.askyesno("Confirm", "Remove the selected Quick Action?"):
                    return
                self.quick_actions.pop(idx)
                self._save_quick_actions()
                self.render_quick_actions()
                refresh_list()

        buttons = ttk.Frame(container)
        buttons.pack(fill="x", pady=(10, 0))
        ttk.Button(buttons, text="Add",    style="Primary.TButton", command=add_action).pack(side="left")
        ttk.Button(buttons, text="Remove", style="Danger.TButton",  command=remove_action).pack(side="left", padx=6)
        ttk.Button(buttons, text="Close",  style="Info.TButton",    command=manager.destroy).pack(side="right")
        refresh_list()

    # ==========================================================================
    # Feature management (admin)
    # ==========================================================================

    def _can_access(self, feature: str) -> bool:
        return self.current_role in self.feature_access.get(feature, [])

    def show_feature_management_panel(self):
        self.clear_root()
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Feature Management", font=("Arial", 16, "bold")).pack(pady=(0, 20))

        roles    = ["admin", "manager", "staff", "viewer"]
        features = list(self.feature_access.keys())
        self._feature_vars: dict = {}
        for feat in features:
            row = ttk.Frame(frame)
            row.pack(fill="x", pady=4)
            ttk.Label(row, text=feat.capitalize(), width=18).pack(side="left")
            self._feature_vars[feat] = {}
            for role in roles:
                var = tk.BooleanVar(value=role in self.feature_access[feat])
                self._feature_vars[feat][role] = var
                ttk.Checkbutton(row, text=role.capitalize(), variable=var).pack(side="left", padx=4)

        def save():
            for feat in features:
                self.feature_access[feat] = [r for r in roles if self._feature_vars[feat][r].get()]
            messagebox.showinfo("Saved", "Feature access updated.")

        ttk.Button(frame, text="Save", command=save, style="Success.TButton").pack(pady=20)

    # ==========================================================================
    # Responsive layout helpers
    # ==========================================================================

    def _apply_responsive_geometry(self):
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        w  = max(1024, min(int(sw * 0.9), sw))
        h  = max(720,  min(int(sh * 0.88), sh))
        x  = max(0, (sw - w) // 2)
        y  = max(0, (sh - h) // 2)
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        self.root.minsize(1024, 720)

    def _on_root_resize(self, event):
        if event.widget is self.root:
            self._apply_sidebar_responsive()
            self._apply_top_nav_responsive()

    def _apply_top_nav_responsive(self):
        width   = self.root.winfo_width()
        compact = width < 1380
        very    = width < 1200

        if compact != self._topnav_compact:
            self._topnav_compact = compact
            for base_name, btn in self.nav_buttons.items():
                full = self.nav_button_texts.get(base_name, base_name)
                btn.configure(text=full.split(" ", 1)[0] if compact else full)
            if hasattr(self, "help_btn"):
                self.help_btn.configure(text="❓" if compact else "Help")
            if hasattr(self, "dark_mode_toggle"):
                self.dark_mode_toggle.configure(text="🌙" if compact else "Dark Mode")

        if hasattr(self, "user_label") and hasattr(self, "logout_btn"):
            if very and self.user_label.winfo_manager():
                self.user_label.pack_forget()
            elif not very and not self.user_label.winfo_manager():
                self.user_label.pack(side="left", padx=8, before=self.logout_btn)

    def _apply_sidebar_responsive(self):
        if not hasattr(self, "sidebar"):
            return
        compact = self.root.winfo_width() < 1280
        if compact != self._sidebar_compact:
            self._sidebar_compact = compact
            self.sidebar.configure(width=104 if compact else 220)
            if hasattr(self, "sidebar_title_label"):
                self.sidebar_title_label.configure(text="Actions" if compact else "Quick Actions")
            if hasattr(self, "manage_actions_btn"):
                self.manage_actions_btn.configure(text="⚙️" if compact else "⚙️ Manage Actions")
            self.render_quick_actions()

    # ==========================================================================
    # Login logo helpers
    # ==========================================================================

    def _load_login_logo(self):
        try:
            assets_dir = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "../../../assets"))
            os.makedirs(assets_dir, exist_ok=True)
            logo_path = os.path.join(assets_dir, "bizhub_logo.png")
            self._generate_logo_image(logo_path)
            img = Image.open(logo_path)
            resample = getattr(Image, "LANCZOS", getattr(Image, "ANTIALIAS", 1))
            img = img.resize((220, 70), resample)
            return ImageTk.PhotoImage(img)
        except Exception:
            return None

    def _generate_logo_image(self, path: str):
        w, h   = 440, 140
        purple = (109, 40, 217, 255)
        dark   = (17,  24,  39,  255)

        img  = Image.new("RGBA", (w, h), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)

        # Icon
        isz  = 110
        ix   = 10
        iy   = (h - isz) // 2
        draw.rounded_rectangle([ix, iy, ix + isz, iy + isz], radius=24, fill=purple)

        # Shared stem
        sx, sy = ix + 26, iy + 18
        sw2, sh2 = 16, isz - 36
        draw.rounded_rectangle([sx, sy, sx + sw2, sy + sh2], radius=8, fill=(255, 255, 255, 255))

        # B bowls
        bw, bh = 44, 28
        bx = sx + sw2 - 4
        draw.rounded_rectangle([bx, sy + 2,       bx + bw, sy + 2 + bh],             radius=14, fill=(255, 255, 255, 255))
        draw.rounded_rectangle([bx, sy + sh2 - bh - 2, bx + bw, sy + sh2 - 2], radius=14, fill=(255, 255, 255, 255))

        # H right stem + crossbar
        hx = ix + isz - 26 - sw2
        draw.rounded_rectangle([hx, sy, hx + sw2, sy + sh2], radius=8, fill=(255, 255, 255, 255))
        cy = iy + isz // 2 - 6
        draw.rounded_rectangle([sx + sw2 - 2, cy, hx + 2, cy + 12], radius=6, fill=(255, 255, 255, 255))

        # Text
        try:
            font_brand = ImageFont.truetype("Arial Bold.ttf", 56)
            font_tag   = ImageFont.truetype("Arial.ttf", 22)
        except Exception:
            font_brand = ImageFont.load_default()
            font_tag   = ImageFont.load_default()

        tx = ix + isz + 16
        ty = iy + 12
        draw.text((tx, ty),      "BzHub", fill=dark,   font=font_brand)
        draw.text((tx, ty + 62), "ERP",   fill=purple, font=font_tag)

        img.save(path)
