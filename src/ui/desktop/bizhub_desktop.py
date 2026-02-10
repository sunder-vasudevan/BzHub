"""BizHub Desktop Application - Tkinter UI refactored to use services."""
import json
import os
import subprocess
import tempfile
import traceback
import shutil
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from PIL import Image, ImageDraw, ImageFont, ImageTk

from src.db import SQLiteAdapter
from src.services import (
    AuthService, InventoryService, POSService, HRService,
    VisitorService, EmailService, ActivityService, CompanyService, AnalyticsService,
    PayrollService, AppraisalService
)
from src.core import CurrencyFormatter, HRCalculator


class BizHubDesktopApp:
    """Main BizHub desktop application using Tkinter."""
    
    def __init__(self, root, db_file="inventory.db"):
        self.root = root
        self.root.title("BzHub - Complete ERP Suite")
        self.root.geometry("1200x800")
        
        # Initialize database and services
        self.db = SQLiteAdapter(db_file)
        self.auth_service = AuthService(self.db)
        self.inventory_service = InventoryService(self.db)
        self.pos_service = POSService(self.db)
        self.hr_service = HRService(self.db)
        self.payroll_service = PayrollService(self.db)
        self.appraisal_service = AppraisalService(self.db)
        self.visitor_service = VisitorService(self.db)
        self.email_service = EmailService(self.db)
        self.activity_service = ActivityService(self.db)
        self.company_service = CompanyService(self.db)
        self.analytics_service = AnalyticsService(self.db)
        
        # Session state
        self.current_user = None
        self.current_role = None

        # Theme
        self.dark_mode = tk.BooleanVar(value=False)
        self.colors = {}

        # POS state
        self.pos_cart = []
        self.pos_selected_item = None
        self.pos_qty_var = tk.StringVar(value="1")
        self.last_receipt_text = None
        self.last_receipt_time = None

        # UI state
        self.tab_index = {}
        self.quick_actions = self._load_quick_actions()
        self._dashboard_sales_trend = []
        self._dashboard_sales_summary = []
        self._reports_trend = []
        self._reports_summary = []
        
        # Setup
        self.setup_styles()
        self.show_login_screen()
    
    def setup_styles(self):
        """Setup UI styles."""
        self.apply_theme()

    def apply_theme(self):
        """Apply light/dark theme styles."""
        light = {
            "bg": "#F5F6FA",
            "card": "#FFFFFF",
            "text": "#111827",
            "muted": "#6B7280",
            "primary": "#6D28D9",
            "accent": "#22D3EE",
            "nav_bg": "#FFFFFF",
            "sidebar_bg": "#F3F4F6",
            "border": "#E5E7EB",
        }
        dark = {
            "bg": "#0B1020",
            "card": "#111827",
            "text": "#F9FAFB",
            "muted": "#9CA3AF",
            "primary": "#8B5CF6",
            "accent": "#22D3EE",
            "nav_bg": "#0F172A",
            "sidebar_bg": "#0F172A",
            "border": "#1F2937",
        }
        self.colors = dark if self.dark_mode.get() else light

        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        self.root.configure(bg=self.colors["bg"])

        style.configure("TFrame", background=self.colors["bg"])
        style.configure("Card.TFrame", background=self.colors["card"])
        style.configure("TLabel", background=self.colors["bg"], foreground=self.colors["text"])
        style.configure("Card.TLabel", background=self.colors["card"], foreground=self.colors["text"])
        style.configure("Header.TLabel", background=self.colors["bg"], foreground=self.colors["text"], font=("Arial", 16, "bold"))
        style.configure("Subheader.TLabel", background=self.colors["bg"], foreground=self.colors["muted"], font=("Arial", 10))

        style.configure("Nav.TButton", foreground=self.colors["text"], background=self.colors["nav_bg"], padding=6)
        style.map("Nav.TButton",
                  background=[("active", self.colors["primary"])],
                  foreground=[("active", "white")])

        style.configure("Sidebar.TButton", foreground=self.colors["text"], background=self.colors["sidebar_bg"], padding=6)
        style.map("Sidebar.TButton",
                  background=[("active", self.colors["primary"])],
                  foreground=[("active", "white")])

        style.configure("Success.TButton", foreground="white", background=self.colors["primary"], padding=6)
        style.map("Success.TButton",
                  background=[("active", self.colors["accent"])])

        style.configure("Danger.TButton", foreground="white", background="#EF4444", padding=6)
        style.map("Danger.TButton",
                  background=[("active", "#DC2626")])

        style.configure("Primary.TButton", foreground="white", background=self.colors["primary"], padding=6)
        style.map("Primary.TButton",
                  background=[("active", self.colors["accent"])])

        style.configure("Info.TButton", foreground=self.colors["text"], background=self.colors["card"], padding=6)

        style.configure("Treeview",
                        background=self.colors["card"],
                        fieldbackground=self.colors["card"],
                        foreground=self.colors["text"],
                        bordercolor=self.colors["border"],
                        rowheight=24)
        style.map("Treeview", background=[("selected", self.colors["primary"])], foreground=[("selected", "white")])
        style.configure("Treeview.Heading", background=self.colors["bg"], foreground=self.colors["text"], relief="flat")

        style.configure("App.TNotebook", background=self.colors["bg"], borderwidth=0)
        style.layout("App.TNotebook.Tab", [])
    
    def clear_root(self):
        """Clear all widgets."""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def show_login_screen(self):
        """Display login screen."""
        self.root.geometry("520x520")
        self.root.minsize(520, 520)
        self.clear_root()
        self.apply_theme()
        
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(fill="both", expand=True)

        logo_img = self._load_login_logo()
        if logo_img:
            logo_label = tk.Label(frame, image=logo_img, bg=self.colors["bg"])
            logo_label.image = logo_img
            logo_label.pack(pady=(0, 10))
        
        ttk.Label(frame, text="Complete ERP Suite", font=("Arial", 10)).pack(pady=(10, 20))
        
        ttk.Label(frame, text="Username:").pack(anchor="w", pady=(10, 0))
        username_entry = ttk.Entry(frame, width=30)
        username_entry.pack(pady=(0, 15), fill="x")
        
        ttk.Label(frame, text="Password:").pack(anchor="w", pady=(10, 0))
        password_entry = ttk.Entry(frame, width=30, show="*")
        password_entry.pack(pady=(0, 20), fill="x")
        
        def login():
            if not username_entry.winfo_exists():
                return
            username = username_entry.get().strip()
            password = password_entry.get()
            
            if not username or not password:
                messagebox.showerror("Error", "Username and password required")
                return
            
            if self.auth_service.authenticate(username, password):
                self.current_user = username
                self.current_role = self.auth_service.get_user_role(username)
                self.auth_service.update_last_login(username)
                self.activity_service.log(username, "Login", f"User logged in")
                self.root.unbind("<Return>")
                self.show_main_ui()
            else:
                messagebox.showerror("Login Failed", "Invalid credentials")
        
        ttk.Button(frame, text="Login", command=login, style="Success.TButton").pack(pady=10, fill="x")
        ttk.Button(frame, text="Exit", command=self.root.quit, style="Danger.TButton").pack(fill="x")

        self.root.bind("<Return>", lambda _e: login())
        username_entry.bind("<Return>", lambda _e: login())
        password_entry.bind("<Return>", lambda _e: login())
        
        username_entry.focus()
    
    def show_main_ui(self):
        """Display main application UI."""
        self._apply_responsive_geometry()
        self.clear_root()
        self.apply_theme()

        # Top Navigation
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

        self.nav_buttons = {}
        nav_items = ["📊 Dashboard", "📇 CRM", "👔 HR", "⚙️ Settings"]
        for name in nav_items:
            base_name = name.split(" ", 1)[1]
            if base_name in {"Dashboard", "Reports", "HR", "Settings"} and self.current_role != "admin":
                continue
            btn = ttk.Button(nav_frame, text=name, style="Nav.TButton",
                             command=lambda n=base_name: self.select_tab(n))
            btn.pack(side="left", padx=4)
            self.nav_buttons[base_name] = btn

        right_frame = tk.Frame(self.top_nav, bg=self.colors["nav_bg"])
        right_frame.pack(side="right", padx=16)

        ttk.Button(right_frame, text="Help", command=self.open_help, style="Info.TButton").pack(side="left", padx=8)
        ttk.Checkbutton(right_frame, text="Dark Mode", variable=self.dark_mode,
                        command=self.toggle_dark_mode).pack(side="left", padx=12)
        ttk.Label(right_frame, text=f"{self.current_user}", style="TLabel").pack(side="left", padx=8)
        ttk.Button(right_frame, text="Logout", command=self.logout, style="Danger.TButton").pack(side="left")

        # Main layout
        main_layout = tk.Frame(self.root, bg=self.colors["bg"])
        main_layout.pack(fill="both", expand=True)

        # Sidebar
        self.sidebar = tk.Frame(main_layout, bg=self.colors["sidebar_bg"], width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        tk.Label(self.sidebar, text="Quick Actions", fg=self.colors["text"], bg=self.colors["sidebar_bg"],
                 font=("Arial", 10, "bold")).pack(anchor="w", padx=12, pady=(12, 8))
        self.quick_actions_container = tk.Frame(self.sidebar, bg=self.colors["sidebar_bg"])
        self.quick_actions_container.pack(fill="x")
        self.render_quick_actions()

        ttk.Button(self.sidebar, text="⚙️ Manage Actions", style="Sidebar.TButton",
               command=self.open_quick_actions_manager).pack(fill="x", padx=10, pady=(10, 4))

        # Content area
        content = tk.Frame(main_layout, bg=self.colors["bg"])
        content.pack(side="left", fill="both", expand=True, padx=12, pady=12)

        # Main notebook (tabs hidden)
        self.notebook = ttk.Notebook(content, style="App.TNotebook")
        self.notebook.pack(fill="both", expand=True)

        # Tabs based on role
        self.tab_index = {}
        if self.current_role == "admin":
            self.create_dashboard_tab()
        self.create_crm_tab()
        if self.current_role == "admin":
            self.create_hr_tab()
            self.create_settings_tab()

        # Default selection
        self.select_tab("Dashboard" if self.current_role == "admin" else "Inventory")
        self.root.bind("<F1>", lambda _e: self.open_help())

    def _apply_responsive_geometry(self):
        """Set window size based on screen size for laptop compatibility."""
        self.root.update_idletasks()
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        width = int(screen_w * 0.9)
        height = int(screen_h * 0.88)

        width = max(1024, min(width, screen_w))
        height = max(720, min(height, screen_h))

        x = max(0, (screen_w - width) // 2)
        y = max(0, (screen_h - height) // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        self.root.minsize(1024, 720)

    def _resize_figure(self, event, figure, canvas):
        """Resize a Matplotlib figure to match the canvas size."""
        if event.width < 50 or event.height < 50:
            return
        dpi = figure.get_dpi()
        figure.set_size_inches(event.width / dpi, event.height / dpi, forward=False)
        font_size = max(6, min(11, int(event.height / 25)))
        for ax in figure.axes:
            ax.tick_params(axis="x", labelsize=font_size, colors=self.colors["text"])
            ax.tick_params(axis="y", labelsize=font_size, colors=self.colors["text"])
            ax.spines["left"].set_color(self.colors["border"])
            ax.spines["bottom"].set_color(self.colors["border"])
        try:
            figure.tight_layout()
        except Exception:
            pass
        canvas.draw_idle()

    def _draw_sales_trend(self, ax, trend):
        """Draw sales trend chart on the given axes."""
        ax.clear()
        ax.set_facecolor(self.colors["card"])
        if trend:
            dates = [d[0] for d in trend]
            totals = [d[1] for d in trend]
            ax.plot(dates, totals, color=self.colors["primary"], linewidth=2)
            ax.fill_between(dates, totals, color=self.colors["accent"], alpha=0.2)
            ax.tick_params(axis="x", labelrotation=45, labelsize=8, colors=self.colors["text"])
            ax.tick_params(axis="y", labelsize=8, colors=self.colors["text"])
        else:
            ax.text(0.5, 0.5, "No sales data", color=self.colors["muted"], ha="center", va="center")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color(self.colors["border"])
        ax.spines["bottom"].set_color(self.colors["border"])

    def _draw_top_items(self, ax, summary):
        """Draw top items bar chart on the given axes."""
        ax.clear()
        ax.set_facecolor(self.colors["card"])
        top_items = summary[:5] if summary else []
        if top_items:
            labels = [i[0] for i in top_items]
            qtys = [i[1] for i in top_items]
            ax.barh(labels, qtys, color=self.colors["primary"])
            ax.tick_params(axis="x", labelsize=8, colors=self.colors["text"])
            ax.tick_params(axis="y", labelsize=8, colors=self.colors["text"])
        else:
            ax.text(0.5, 0.5, "No sales data", color=self.colors["muted"], ha="center", va="center")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color(self.colors["border"])
        ax.spines["bottom"].set_color(self.colors["border"])

    def open_chart_zoom(self, title, draw_fn):
        """Open a larger view of a chart; click to close."""
        zoom = tk.Toplevel(self.root)
        zoom.title(title)
        zoom.geometry("900x600")
        zoom.minsize(700, 500)

        frame = tk.Frame(zoom, bg=self.colors["bg"])
        frame.pack(fill="both", expand=True, padx=12, pady=12)
        tk.Label(frame, text=title, bg=self.colors["bg"], fg=self.colors["text"],
                 font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 8))

        fig = Figure(figsize=(7, 4), dpi=100)
        ax = fig.add_subplot(111)
        draw_fn(ax)
        fig.patch.set_facecolor(self.colors["card"])

        canvas = FigureCanvasTkAgg(fig, master=frame)
        widget = canvas.get_tk_widget()
        widget.pack(fill="both", expand=True)
        widget.bind("<Configure>", lambda e: self._resize_figure(e, fig, canvas))
        widget.bind("<Button-1>", lambda _e: zoom.destroy())
        canvas.draw()

    def _load_login_logo(self):
        """Create or load BzHub logo for the login screen."""
        try:
            assets_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "assets")
            assets_dir = os.path.abspath(assets_dir)
            os.makedirs(assets_dir, exist_ok=True)
            logo_path = os.path.join(assets_dir, "bizhub_logo.png")

            self._generate_logo_image(logo_path)

            img = Image.open(logo_path)
            img = img.resize((220, 70), Image.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception:
            return None

    def _generate_logo_image(self, path):
        """Generate a simple BizHub logo (text + icon) in theme colors."""
        width, height = 440, 140
        bg = (255, 255, 255, 0)
        purple = (109, 40, 217, 255)  # #6D28D9
        dark = (17, 24, 39, 255)      # #111827

        img = Image.new("RGBA", (width, height), bg)
        draw = ImageDraw.Draw(img)

        # Icon: rounded square with shared-stem BH monogram
        icon_size = 110
        icon_x = 10
        icon_y = (height - icon_size) // 2
        draw.rounded_rectangle([icon_x, icon_y, icon_x + icon_size, icon_y + icon_size], radius=24, fill=purple)

        # Shared stem
        stem_x = icon_x + 26
        stem_y = icon_y + 18
        stem_w = 16
        stem_h = icon_size - 36
        draw.rounded_rectangle([stem_x, stem_y, stem_x + stem_w, stem_y + stem_h], radius=8, fill=(255, 255, 255, 255))

        # B bowls (top and bottom)
        bowl_w = 44
        bowl_h = 28
        bowl_x = stem_x + stem_w - 4
        top_y = stem_y + 2
        bot_y = stem_y + stem_h - bowl_h - 2
        draw.rounded_rectangle([bowl_x, top_y, bowl_x + bowl_w, top_y + bowl_h], radius=14, fill=(255, 255, 255, 255))
        draw.rounded_rectangle([bowl_x, bot_y, bowl_x + bowl_w, bot_y + bowl_h], radius=14, fill=(255, 255, 255, 255))

        # H right stem + crossbar
        h_stem_x = icon_x + icon_size - 26 - stem_w
        draw.rounded_rectangle([h_stem_x, stem_y, h_stem_x + stem_w, stem_y + stem_h], radius=8, fill=(255, 255, 255, 255))
        cross_y = icon_y + icon_size // 2 - 6
        draw.rounded_rectangle([stem_x + stem_w - 2, cross_y, h_stem_x + 2, cross_y + 12], radius=6, fill=(255, 255, 255, 255))

        # Brand text
        try:
            font_brand = ImageFont.truetype("Arial Bold.ttf", 56)
            font_tag = ImageFont.truetype("Arial.ttf", 22)
        except Exception:
            font_brand = ImageFont.load_default()
            font_tag = ImageFont.load_default()

        brand_x = icon_x + icon_size + 16
        brand_y = icon_y + 12
        draw.text((brand_x, brand_y), "BzHub", fill=dark, font=font_brand)
        draw.text((brand_x, brand_y + 62), "ERP", fill=purple, font=font_tag)

        img.save(path)

    def select_tab(self, name: str):
        """Select a tab by name."""
        try:
            if name in self.tab_index:
                self.notebook.select(self.tab_index[name])
                self.notebook.update_idletasks()
            elif hasattr(self, "crm_tab_index") and name in self.crm_tab_index:
                self.notebook.select(self.tab_index.get("CRM"))
                self.notebook.update_idletasks()
                self.crm_notebook.select(self.crm_tab_index[name])
                self.crm_notebook.update_idletasks()
            if name == "Dashboard" and self.current_role == "admin":
                self.refresh_dashboard()
            if name == "HR" and self.current_role == "admin":
                self.refresh_hr_cards()
            if name == "Bills":
                self.refresh_bills_timeline()
            if name == "Visitors":
                self.refresh_visitors_cards()
            if name == "Reports" and self.current_role == "admin":
                self.refresh_reports()
        except Exception as e:
            try:
                logs_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "logs")
                logs_dir = os.path.abspath(logs_dir)
                os.makedirs(logs_dir, exist_ok=True)
                log_path = os.path.join(logs_dir, "ui_errors.log")
                with open(log_path, "a", encoding="utf-8") as f:
                    f.write("\n=== UI Navigation Error ===\n")
                    f.write(f"Tab: {name}\n")
                    f.write(traceback.format_exc())
            except Exception:
                log_path = "(log unavailable)"
            messagebox.showerror("Navigation Error", f"Failed to open {name}: {e}\nLog: {log_path}")

    def open_help(self):
        """Open context-sensitive help dialog."""
        help_text = self._load_help_text()
        context = self._get_help_context()
        section_title = self._get_help_section_title(context)
        if section_title:
            content = self._extract_help_section(help_text, section_title)
            title = f"Help: {section_title}"
        else:
            content = help_text
            title = "BzHub Help"
        self._show_help_dialog(title, content)

    def _get_help_context(self) -> str:
        """Determine current UI context for help."""
        main_tab = self._get_selected_tab_name(self.notebook, self.tab_index)
        if main_tab == "CRM" and hasattr(self, "crm_notebook"):
            sub_tab = self._get_selected_tab_name(self.crm_notebook, self.crm_tab_index)
            return f"CRM/{sub_tab}" if sub_tab else "CRM"
        if main_tab == "HR" and hasattr(self, "hr_notebook") and hasattr(self, "hr_tab_index"):
            sub_tab = self._get_selected_tab_name(self.hr_notebook, self.hr_tab_index)
            return f"HR/{sub_tab}" if sub_tab else "HR"
        return main_tab or ""

    def _get_selected_tab_name(self, notebook, mapping) -> str:
        """Get selected tab name for a notebook using mapping."""
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
        """Map UI context to help section title."""
        mapping = {
            "Dashboard": "Dashboard",
            "CRM": "CRM",
            "CRM/Inventory": "Inventory (CRM)",
            "CRM/POS": "POS (CRM)",
            "CRM/Reports": "Reports (CRM)",
            "CRM/Bills": "Bills (CRM)",
            "CRM/Visitors": "Visitors (CRM)",
            "HR": "HR",
            "HR/Employees": "Employees (HR)",
            "HR/Payroll": "Payroll (HR)",
            "HR/Appraisals": "Appraisals (HR)",
            "HR/Feedback": "Feedback (HR)",
            "Settings": "Settings",
        }
        return mapping.get(context, "")

    def _load_help_text(self) -> str:
        """Load help content from documentation file."""
        help_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "documentation", "HELP.md")
        help_path = os.path.abspath(help_path)
        try:
            with open(help_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            return "BzHub help content is unavailable."

    def _extract_help_section(self, text: str, title: str) -> str:
        """Extract a section by heading title from markdown text."""
        lines = text.splitlines()
        start = None
        level = None
        target = title.strip().lower()
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("#"):
                hashes = len(stripped) - len(stripped.lstrip("#"))
                heading = stripped.strip("# ").strip().lower()
                if heading == target:
                    start = i
                    level = hashes
                    break
        if start is None:
            return text
        end = len(lines)
        for j in range(start + 1, len(lines)):
            stripped = lines[j].strip()
            if stripped.startswith("#"):
                hashes = len(stripped) - len(stripped.lstrip("#"))
                if hashes <= level:
                    end = j
                    break
        return "\n".join(lines[start:end]).strip()

    def _show_help_dialog(self, title: str, content: str):
        """Show help content in a dialog."""
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("760x560")
        dialog.configure(bg=self.colors["bg"])
        dialog.transient(self.root)
        dialog.grab_set()

        header = tk.Frame(dialog, bg=self.colors["bg"])
        header.pack(fill="x", padx=12, pady=(12, 6))
        tk.Label(header, text=title, bg=self.colors["bg"], fg=self.colors["text"],
                 font=("Arial", 12, "bold")).pack(side="left")

        body = tk.Frame(dialog, bg=self.colors["bg"])
        body.pack(fill="both", expand=True, padx=12, pady=6)

        scrollbar = ttk.Scrollbar(body, orient="vertical")
        text = tk.Text(body, wrap="word", yscrollcommand=scrollbar.set,
                       bg=self.colors["card"], fg=self.colors["text"],
                       insertbackground=self.colors["text"], relief="flat")
        scrollbar.config(command=text.yview)
        scrollbar.pack(side="right", fill="y")
        text.pack(side="left", fill="both", expand=True)

        text.insert("1.0", content)
        text.config(state="disabled")

        footer = tk.Frame(dialog, bg=self.colors["bg"])
        footer.pack(fill="x", padx=12, pady=(6, 12))
        ttk.Button(footer, text="Close", style="Info.TButton", command=dialog.destroy).pack(side="right")

    def toggle_dark_mode(self):
        """Toggle dark mode and refresh UI."""
        self.apply_theme()
        self.show_main_ui()

    def show_low_stock_popup(self):
        """Show low stock items in a quick popup."""
        items = self.inventory_service.get_low_stock_items()
        if not items:
            messagebox.showinfo("Low Stock", "No low stock items found.")
            return
        msg = "\n".join([f"- {i[0]} (Qty: {i[1]}, Threshold: {i[2]})" for i in items[:10]])
        messagebox.showinfo("Low Stock", msg)

    # === Quick Actions helpers ===
    def _get_quick_actions_path(self):
        assets_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "assets")
        assets_dir = os.path.abspath(assets_dir)
        os.makedirs(assets_dir, exist_ok=True)
        return os.path.join(assets_dir, "quick_actions.json")

    def _default_quick_actions(self):
        return [
            {"label": "➕ Add Item", "target": "Inventory"},
            {"label": "🧾 New Sale", "target": "POS"},
            {"label": "⚠️ Low Stock", "target": "low_stock"},
            {"label": "📈 Projections", "target": "Dashboard"},
        ]

    def _load_quick_actions(self):
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
        path = self._get_quick_actions_path()
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.quick_actions, f, indent=2)
        except Exception:
            pass

    def render_quick_actions(self):
        if not hasattr(self, "quick_actions_container"):
            return
        for widget in self.quick_actions_container.winfo_children():
            widget.destroy()

        for action in self.quick_actions:
            target = action.get("target")
            if target in {"Dashboard", "Reports", "HR", "Settings"} and self.current_role != "admin":
                continue
            label = action.get("label") or target
            ttk.Button(self.quick_actions_container, text=label, style="Sidebar.TButton",
                       command=lambda t=target: self.handle_quick_action(t)).pack(fill="x", padx=10, pady=4)

    def handle_quick_action(self, target: str):
        if target == "low_stock":
            self.show_low_stock_popup()
            return
        self.select_tab(target)

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

        listbox = tk.Listbox(list_frame, height=10)
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
        action_combo = ttk.Combobox(form, values=action_options, textvariable=action_var, state="readonly")
        action_combo.grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=(8, 0))

        form.columnconfigure(1, weight=1)

        buttons = ttk.Frame(container)
        buttons.pack(fill="x", pady=(10, 0))

        def refresh_list():
            listbox.delete(0, tk.END)
            for a in self.quick_actions:
                label = a.get("label") or a.get("target")
                target = a.get("target")
                display_target = "Low Stock" if target == "low_stock" else target
                listbox.insert(tk.END, f"{label} → {display_target}")

        def add_action():
            label = label_entry.get().strip()
            target_label = action_var.get()
            target = "low_stock" if target_label == "Low Stock" else target_label
            if not label:
                label = target_label
            self.quick_actions.append({"label": label, "target": target})
            self._save_quick_actions()
            self.render_quick_actions()
            refresh_list()
            label_entry.delete(0, tk.END)

        def remove_action():
            selection = listbox.curselection()
            if not selection:
                return
            idx = selection[0]
            if 0 <= idx < len(self.quick_actions):
                messagebox.showwarning("Caution", "You are about to remove a Quick Action.")
                if not messagebox.askyesno("Confirm", "Remove the selected Quick Action?"):
                    return
                self.quick_actions.pop(idx)
                self._save_quick_actions()
                self.render_quick_actions()
                refresh_list()

        ttk.Button(buttons, text="Add", style="Primary.TButton", command=add_action).pack(side="left")
        ttk.Button(buttons, text="Remove", style="Danger.TButton", command=remove_action).pack(side="left", padx=6)
        ttk.Button(buttons, text="Close", style="Info.TButton", command=manager.destroy).pack(side="right")

        refresh_list()
    
    def logout(self):
        """Logout user."""
        self.activity_service.log(self.current_user, "Logout", "User logged out")
        self.current_user = None
        self.current_role = None
        self.show_login_screen()

    def create_crm_tab(self):
        """Create CRM tab with nested modules."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="📇 CRM")
        self.tab_index["CRM"] = frame

        container = tk.Frame(frame, bg=self.colors["bg"])
        container.pack(fill="both", expand=True)

        self.crm_notebook = ttk.Notebook(container)
        self.crm_notebook.pack(fill="both", expand=True)

        self.crm_tab_index = {}
        self.create_inventory_tab(self.crm_notebook)
        self.create_pos_tab(self.crm_notebook)
        if self.current_role == "admin":
            self.create_reports_tab(self.crm_notebook)
        self.create_bills_tab(self.crm_notebook)
        self.create_visitors_tab(self.crm_notebook)
    
    def create_dashboard_tab(self):
        """Create dashboard tab (admin only)."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="📊 Dashboard")
        self.tab_index["Dashboard"] = frame

        container = tk.Frame(frame, bg=self.colors["bg"])
        container.pack(fill="both", expand=True, padx=12, pady=12)

        header = tk.Frame(container, bg=self.colors["bg"])
        header.pack(fill="x", pady=(0, 12))

        ttk.Label(header, text="📊 Dashboard", style="Header.TLabel").pack(side="left")

        period_frame = tk.Frame(header, bg=self.colors["bg"])
        period_frame.pack(side="right")
        ttk.Label(period_frame, text="Projection Window", style="Subheader.TLabel").pack(side="left", padx=(0, 8))

        self.dashboard_period_var = tk.StringVar(value="Last 7 Days")
        self.period_map = {
            "Last 7 Days": "7",
            "Last 30 Days": "30",
            "Quarter": "90",
            "Year": "365",
        }
        self.period_combo = ttk.Combobox(period_frame, values=list(self.period_map.keys()),
                                         textvariable=self.dashboard_period_var, state="readonly", width=16)
        self.period_combo.pack(side="left")
        self.period_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_dashboard())

        # KPI Cards
        kpi_row = tk.Frame(container, bg=self.colors["bg"])
        kpi_row.pack(fill="x", pady=(0, 12))

        self.kpi_labels = {}
        self.kpi_labels["sales"] = self._create_kpi_card(kpi_row, "Sales (Period)")
        self.kpi_labels["inventory"] = self._create_kpi_card(kpi_row, "Inventory Value")
        self.kpi_labels["low_stock"] = self._create_kpi_card(kpi_row, "Low Stock Items")
        self.kpi_labels["visitors"] = self._create_kpi_card(kpi_row, "Visitors")

        # Charts
        charts_row = tk.Frame(container, bg=self.colors["bg"])
        charts_row.pack(fill="both", expand=True)

        sales_chart_card = tk.Frame(charts_row, bg=self.colors["card"], padx=12, pady=12)
        sales_chart_card.pack(side="left", fill="both", expand=True, padx=(0, 8))
        tk.Label(sales_chart_card, text="Sales Trend", bg=self.colors["card"], fg=self.colors["text"],
                 font=("Arial", 10, "bold")).pack(anchor="w")

        self.sales_fig = Figure(figsize=(5, 3), dpi=100)
        self.sales_ax = self.sales_fig.add_subplot(111)
        self.sales_canvas = FigureCanvasTkAgg(self.sales_fig, master=sales_chart_card)
        self.sales_canvas.get_tk_widget().pack(fill="both", expand=True)
        self.sales_canvas.get_tk_widget().bind(
            "<Configure>",
            lambda e: self._resize_figure(e, self.sales_fig, self.sales_canvas)
        )
        self.sales_canvas.get_tk_widget().bind(
            "<Double-1>",
            lambda _e: self.open_chart_zoom("Sales Trend", lambda ax: self._draw_sales_trend(ax, self._dashboard_sales_trend))
        )

        top_items_card = tk.Frame(charts_row, bg=self.colors["card"], padx=12, pady=12)
        top_items_card.pack(side="left", fill="both", expand=True, padx=(8, 0))
        tk.Label(top_items_card, text="Top Selling Items", bg=self.colors["card"], fg=self.colors["text"],
                 font=("Arial", 10, "bold")).pack(anchor="w")

        self.top_fig = Figure(figsize=(5, 3), dpi=100)
        self.top_ax = self.top_fig.add_subplot(111)
        self.top_canvas = FigureCanvasTkAgg(self.top_fig, master=top_items_card)
        self.top_canvas.get_tk_widget().pack(fill="both", expand=True)
        self.top_canvas.get_tk_widget().bind(
            "<Configure>",
            lambda e: self._resize_figure(e, self.top_fig, self.top_canvas)
        )
        self.top_canvas.get_tk_widget().bind(
            "<Double-1>",
            lambda _e: self.open_chart_zoom("Top Selling Items", lambda ax: self._draw_top_items(ax, self._dashboard_sales_summary))
        )

        # Tables
        tables_row = tk.Frame(container, bg=self.colors["bg"])
        tables_row.pack(fill="both", expand=True, pady=(12, 0))

        reorder_card = tk.Frame(tables_row, bg=self.colors["card"], padx=12, pady=12)
        reorder_card.pack(side="left", fill="both", expand=True, padx=(0, 8))
        tk.Label(reorder_card, text="Reorder Recommendations", bg=self.colors["card"], fg=self.colors["text"],
                 font=("Arial", 10, "bold")).pack(anchor="w")

        self.reorder_tree = ttk.Treeview(reorder_card, columns=("Item", "Current", "AvgDaily", "Recommend"),
                                         show="headings", height=6)
        for col, text, width in [("Item", "Item", 160), ("Current", "Current Qty", 90),
                                 ("AvgDaily", "Avg Daily", 90), ("Recommend", "Recommend", 90)]:
            self.reorder_tree.heading(col, text=text)
            self.reorder_tree.column(col, anchor="center", width=width)
        self.reorder_tree.pack(fill="both", expand=True, pady=(6, 0))

        low_card = tk.Frame(tables_row, bg=self.colors["card"], padx=12, pady=12)
        low_card.pack(side="left", fill="both", expand=True, padx=(8, 0))
        tk.Label(low_card, text="Low Stock Items", bg=self.colors["card"], fg=self.colors["text"],
                 font=("Arial", 10, "bold")).pack(anchor="w")

        self.low_stock_tree = ttk.Treeview(low_card, columns=("Item", "Qty", "Threshold"),
                                           show="headings", height=6)
        for col, text, width in [("Item", "Item", 180), ("Qty", "Qty", 70), ("Threshold", "Threshold", 90)]:
            self.low_stock_tree.heading(col, text=text)
            self.low_stock_tree.column(col, anchor="center", width=width)
        self.low_stock_tree.pack(fill="both", expand=True, pady=(6, 0))

        self.refresh_dashboard()

    def _create_kpi_card(self, parent, title):
        card = tk.Frame(parent, bg=self.colors["card"], padx=12, pady=12)
        card.pack(side="left", fill="both", expand=True, padx=6)
        tk.Label(card, text=title, bg=self.colors["card"], fg=self.colors["muted"], font=("Arial", 9)).pack(anchor="w")
        value_label = tk.Label(card, text="--", bg=self.colors["card"], fg=self.colors["text"],
                               font=("Arial", 16, "bold"))
        value_label.pack(anchor="w", pady=(6, 0))
        return value_label

    def refresh_dashboard(self):
        """Refresh dashboard data and charts."""
        period_key = self.period_map.get(self.dashboard_period_var.get(), "7")
        start_date, end_date, days = self.analytics_service.get_date_range(period_key)

        sales_trend = self.analytics_service.get_sales_trend(start_date, end_date)
        sales_summary = self.analytics_service.get_sales_summary(start_date, end_date)
        reorder = self.analytics_service.get_reorder_recommendations(start_date, end_date, window_days=7)

        self._dashboard_sales_trend = sales_trend
        self._dashboard_sales_summary = sales_summary

        sales_total = sum(r[1] for r in sales_trend) if sales_trend else 0.0
        inv_value = self.inventory_service.get_inventory_value()
        low_stock = self.inventory_service.get_low_stock_items()
        visitors_count = self.visitor_service.get_total_visitors_count()

        self.kpi_labels["sales"].config(text=CurrencyFormatter.format_currency(sales_total))
        self.kpi_labels["inventory"].config(text=CurrencyFormatter.format_currency(inv_value))
        self.kpi_labels["low_stock"].config(text=str(len(low_stock)))
        self.kpi_labels["visitors"].config(text=str(visitors_count))

        self._draw_sales_trend(self.sales_ax, sales_trend)
        self.sales_fig.patch.set_facecolor(self.colors["card"])
        self.sales_canvas.draw()

        self._draw_top_items(self.top_ax, sales_summary)
        self.top_fig.patch.set_facecolor(self.colors["card"])
        self.top_canvas.draw()

        # Reorder recommendations
        for item in self.reorder_tree.get_children():
            self.reorder_tree.delete(item)
        for item_name, current_qty, avg_daily, recommended in reorder:
            self.reorder_tree.insert('', 'end', values=(item_name, current_qty, f"{avg_daily:.2f}", recommended))

        # Low stock table
        for item in self.low_stock_tree.get_children():
            self.low_stock_tree.delete(item)
        for item in low_stock[:10]:
            self.low_stock_tree.insert('', 'end', values=(item[0], item[1], item[2]))
    
    def create_inventory_tab(self, notebook=None):
        """Create inventory management tab."""
        parent = notebook or self.notebook
        frame = ttk.Frame(parent)
        parent.add(frame, text="📦 Inventory")
        if notebook is not None:
            self.crm_tab_index["Inventory"] = frame
        else:
            self.tab_index["Inventory"] = frame

        container = tk.Frame(frame, bg=self.colors["bg"])
        container.pack(fill="both", expand=True, padx=12, pady=12)

        header = tk.Frame(container, bg=self.colors["bg"])
        header.pack(fill="x", pady=(0, 12))
        ttk.Label(header, text="📦 Inventory", style="Header.TLabel").pack(side="left")
        ttk.Label(header, text="Manage stock, pricing, and thresholds", style="Subheader.TLabel").pack(side="left", padx=10)

        body = tk.Frame(container, bg=self.colors["bg"])
        body.pack(fill="both", expand=True)

        # Left: Form card
        form_card = tk.Frame(body, bg=self.colors["card"], padx=12, pady=12)
        form_card.pack(side="left", fill="y", padx=(0, 10))

        tk.Label(form_card, text="Add / Edit Item", bg=self.colors["card"], fg=self.colors["text"],
                 font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 8))

        def field_row(label_text):
            row = tk.Frame(form_card, bg=self.colors["card"])
            row.pack(fill="x", pady=4)
            tk.Label(row, text=label_text, bg=self.colors["card"], fg=self.colors["muted"], width=12, anchor="w").pack(side="left")
            entry = ttk.Entry(row)
            entry.pack(side="left", fill="x", expand=True)
            return entry

        self.inv_name = field_row("Item Name")
        self.inv_qty = field_row("Quantity")
        self.inv_threshold = field_row("Threshold")
        self.inv_cost = field_row("Cost Price")
        self.inv_sale = field_row("Sale Price")
        self.inv_desc = field_row("Description")

        image_row = tk.Frame(form_card, bg=self.colors["card"])
        image_row.pack(fill="x", pady=4)
        tk.Label(image_row, text="Image", bg=self.colors["card"], fg=self.colors["muted"], width=12, anchor="w").pack(side="left")
        self.inv_image = ttk.Entry(image_row)
        self.inv_image.pack(side="left", fill="x", expand=True)
        ttk.Button(image_row, text="Browse", style="Info.TButton", command=self.browse_inventory_image).pack(side="left", padx=4)

        btn_row = tk.Frame(form_card, bg=self.colors["card"])
        btn_row.pack(fill="x", pady=(10, 0))
        ttk.Button(btn_row, text="Add", command=self.add_inventory_item, style="Success.TButton").pack(side="left", padx=3)
        ttk.Button(btn_row, text="Update", command=self.update_inventory_item, style="Primary.TButton").pack(side="left", padx=3)
        ttk.Button(btn_row, text="Delete", command=self.delete_inventory_item, style="Danger.TButton").pack(side="left", padx=3)
        ttk.Button(btn_row, text="Clear", command=self.clear_inventory_form, style="Info.TButton").pack(side="left", padx=3)

        # Right: List card
        list_card = tk.Frame(body, bg=self.colors["card"], padx=12, pady=12)
        list_card.pack(side="left", fill="both", expand=True)

        list_header = tk.Frame(list_card, bg=self.colors["card"])
        list_header.pack(fill="x")
        tk.Label(list_header, text="Inventory Items", bg=self.colors["card"], fg=self.colors["text"],
                 font=("Arial", 10, "bold")).pack(side="left")

        search_row = tk.Frame(list_card, bg=self.colors["card"])
        search_row.pack(fill="x", pady=(8, 6))
        tk.Label(search_row, text="Search", bg=self.colors["card"], fg=self.colors["muted"]).pack(side="left", padx=(0, 6))
        self.inv_search = ttk.Entry(search_row)
        self.inv_search.pack(side="left", fill="x", expand=True)
        ttk.Button(search_row, text="🔎", command=self.search_inventory, style="Info.TButton").pack(side="left", padx=6)
        ttk.Button(search_row, text="Refresh", command=self.refresh_inventory_list, style="Info.TButton").pack(side="left")

        columns = ("Item", "Qty", "Threshold", "Cost", "Sale", "Description")
        self.inv_tree = ttk.Treeview(list_card, columns=columns, height=18, show="headings")
        for col, width in [("Item", 180), ("Qty", 70), ("Threshold", 90), ("Cost", 90), ("Sale", 90), ("Description", 220)]:
            self.inv_tree.column(col, anchor="center", width=width)
            self.inv_tree.heading(col, text=col)

        self.inv_tree.pack(fill="both", expand=True, pady=(6, 0))
        self.inv_tree.bind("<Double-1>", self.on_inventory_select)

        self.refresh_inventory_list()
    
    def add_inventory_item(self):
        """Add inventory item."""
        try:
            name = self.inv_name.get().strip()
            qty = int(self.inv_qty.get())
            threshold = int(self.inv_threshold.get())
            cost = float(self.inv_cost.get())
            sale = float(self.inv_sale.get())
            desc = self.inv_desc.get().strip()
            image_path = self.inv_image.get().strip() or None
            
            if not name:
                messagebox.showerror("Error", "Item name required")
                return

            if self.inventory_service.add_item(name, qty, threshold, cost, sale, desc, image_path=image_path):
                self.activity_service.log(self.current_user, "Add Inventory", f"Added item: {name}")
                messagebox.showinfo("Success", f"Item '{name}' added")
                self.clear_inventory_form()
                self.refresh_inventory_list()
            else:
                messagebox.showerror("Error", "Failed to add item (may already exist)")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {e}")
    
    def update_inventory_item(self):
        """Update inventory item."""
        try:
            name = self.inv_name.get().strip()
            if not name:
                messagebox.showerror("Error", "Select item to update")
                return
            
            qty = int(self.inv_qty.get()) if self.inv_qty.get() else None
            threshold = int(self.inv_threshold.get()) if self.inv_threshold.get() else None
            cost = float(self.inv_cost.get()) if self.inv_cost.get() else None
            sale = float(self.inv_sale.get()) if self.inv_sale.get() else None
            desc = self.inv_desc.get().strip()
            
            if self.inventory_service.update_item(name, quantity=qty, threshold=threshold, cost_price=cost, sale_price=sale, description=desc if desc else None):
                self.activity_service.log(self.current_user, "Update Inventory", f"Updated item: {name}")
                messagebox.showinfo("Success", "Item updated")
                self.refresh_inventory_list()
            else:
                messagebox.showerror("Error", "Failed to update item")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {e}")
    
    def delete_inventory_item(self):
        """Delete inventory item."""
        name = self.inv_name.get().strip()
        if not name:
            messagebox.showerror("Error", "Select item to delete")
            return

        messagebox.showwarning("Caution", "This will permanently delete the inventory item.")
        if messagebox.askyesno("Confirm", f"Delete '{name}'?"):
            if self.inventory_service.delete_item(name):
                self.activity_service.log(self.current_user, "Delete Inventory", f"Deleted item: {name}")
                messagebox.showinfo("Success", "Item deleted")
                self.clear_inventory_form()
                self.refresh_inventory_list()
            else:
                messagebox.showerror("Error", "Failed to delete item")
    
    def clear_inventory_form(self):
        """Clear inventory form."""
        for entry in [self.inv_name, self.inv_qty, self.inv_threshold, self.inv_cost, self.inv_sale, self.inv_desc, self.inv_image]:
            entry.delete(0, tk.END)

    def browse_inventory_image(self):
        """Select an image for the inventory item and copy it locally."""
        file_path = filedialog.askopenfilename(
            title="Select Item Image",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif *.bmp"), ("All Files", "*.*")]
        )
        if not file_path:
            return
        try:
            images_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "assets", "item_images")
            images_dir = os.path.abspath(images_dir)
            os.makedirs(images_dir, exist_ok=True)
            filename = os.path.basename(file_path)
            dest_path = os.path.join(images_dir, filename)
            if os.path.abspath(file_path) != os.path.abspath(dest_path):
                shutil.copy(file_path, dest_path)
            self.inv_image.delete(0, tk.END)
            self.inv_image.insert(0, dest_path)
        except Exception as e:
            messagebox.showerror("Image", f"Failed to attach image: {e}")
    
    def refresh_inventory_list(self):
        """Refresh inventory list."""
        for item in self.inv_tree.get_children():
            self.inv_tree.delete(item)
        
        items = self.inventory_service.get_all_items()
        for item in items:
            self.inv_tree.insert('', 'end', values=(
                item[0], item[1], item[2],
                CurrencyFormatter.format_currency(item[3]),
                CurrencyFormatter.format_currency(item[4]),
                item[5] or ""
            ))
    
    def search_inventory(self):
        """Search inventory."""
        query = self.inv_search.get().strip()
        for item in self.inv_tree.get_children():
            self.inv_tree.delete(item)
        
        items = self.inventory_service.search(query) if query else self.inventory_service.get_all_items()
        for item in items:
            self.inv_tree.insert('', 'end', values=(
                item[0], item[1], item[2],
                CurrencyFormatter.format_currency(item[3]),
                CurrencyFormatter.format_currency(item[4]),
                item[5] or ""
            ))
    
    def on_inventory_select(self, event):
        """Handle inventory item selection."""
        selection = self.inv_tree.selection()
        if selection:
            item = self.inv_tree.item(selection[0])
            values = item['values']
            self.inv_name.delete(0, tk.END)
            self.inv_name.insert(0, values[0])
            self.inv_qty.delete(0, tk.END)
            self.inv_qty.insert(0, values[1])
            self.inv_threshold.delete(0, tk.END)
            self.inv_threshold.insert(0, values[2])
            self.inv_cost.delete(0, tk.END)
            self.inv_cost.insert(0, values[3].replace("₹", ""))
            self.inv_sale.delete(0, tk.END)
            self.inv_sale.insert(0, values[4].replace("₹", ""))
            self.inv_desc.delete(0, tk.END)
            self.inv_desc.insert(0, values[5])
            details = self.inventory_service.get_item(values[0])
            self.inv_image.delete(0, tk.END)
            if details and details.get("image_path"):
                self.inv_image.insert(0, details.get("image_path"))
    
    def create_pos_tab(self, notebook=None):
        """Create POS tab."""
        parent = notebook or self.notebook
        frame = ttk.Frame(parent)
        parent.add(frame, text="💳 POS")
        if notebook is not None:
            self.crm_tab_index["POS"] = frame
        else:
            self.tab_index["POS"] = frame

        container = tk.Frame(frame, bg=self.colors["bg"])
        container.pack(fill="both", expand=True, padx=12, pady=12)

        header = tk.Frame(container, bg=self.colors["bg"])
        header.pack(fill="x", pady=(0, 12))
        ttk.Label(header, text="💳 POS", style="Header.TLabel").pack(side="left")
        ttk.Label(header, text="Quick add, search, and checkout", style="Subheader.TLabel").pack(side="left", padx=10)

        body = tk.Frame(container, bg=self.colors["bg"])
        body.pack(fill="both", expand=True)

        # Left panel: search + items + quick add
        left = tk.Frame(body, bg=self.colors["card"], padx=12, pady=12)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        tk.Label(left, text="Inventory Search", bg=self.colors["card"], fg=self.colors["text"],
                 font=("Arial", 10, "bold")).pack(anchor="w")
        search_row = tk.Frame(left, bg=self.colors["card"])
        search_row.pack(fill="x", pady=(6, 6))
        self.pos_search_entry = ttk.Entry(search_row)
        self.pos_search_entry.pack(side="left", fill="x", expand=True)
        ttk.Button(search_row, text="Search", style="Info.TButton", command=self.search_pos_items).pack(side="left", padx=6)
        ttk.Button(search_row, text="Reset", style="Info.TButton", command=self.load_pos_items).pack(side="left")

        self.pos_items_tree = ttk.Treeview(left, columns=("Item", "Qty", "Price"), show="headings", height=10)
        for col, text, width in [("Item", "Item", 200), ("Qty", "Qty", 60), ("Price", "Price", 80)]:
            self.pos_items_tree.heading(col, text=text)
            self.pos_items_tree.column(col, anchor="center", width=width)
        self.pos_items_tree.pack(fill="both", expand=True, pady=(4, 8))
        self.pos_items_tree.bind("<Double-1>", self.add_selected_item_to_cart)

        tk.Label(left, text="Quick Add", bg=self.colors["card"], fg=self.colors["text"],
                 font=("Arial", 10, "bold")).pack(anchor="w")
        self.quick_add_frame = tk.Frame(left, bg=self.colors["card"])
        self.quick_add_frame.pack(fill="x", pady=(6, 0))

        # Right panel: cart + totals + numpad
        right = tk.Frame(body, bg=self.colors["card"], padx=12, pady=12)
        right.pack(side="left", fill="both", expand=True)

        tk.Label(right, text="Cart", bg=self.colors["card"], fg=self.colors["text"],
                 font=("Arial", 10, "bold")).pack(anchor="w")

        self.pos_cart_tree = ttk.Treeview(right, columns=("Item", "Qty", "Price", "Total"), show="headings", height=10)
        for col, text, width in [("Item", "Item", 200), ("Qty", "Qty", 60), ("Price", "Price", 80), ("Total", "Total", 90)]:
            self.pos_cart_tree.heading(col, text=text)
            self.pos_cart_tree.column(col, anchor="center", width=width)
        self.pos_cart_tree.pack(fill="both", expand=True, pady=(4, 8))
        self.pos_cart_tree.bind("<Double-1>", self.select_cart_item)

        totals_row = tk.Frame(right, bg=self.colors["card"])
        totals_row.pack(fill="x", pady=(0, 10))
        tk.Label(totals_row, text="Total", bg=self.colors["card"], fg=self.colors["muted"]).pack(side="left")
        self.pos_total_label = tk.Label(totals_row, text=CurrencyFormatter.format_currency(0),
                                        bg=self.colors["card"], fg=self.colors["text"], font=("Arial", 14, "bold"))
        self.pos_total_label.pack(side="right")

        qty_row = tk.Frame(right, bg=self.colors["card"])
        qty_row.pack(fill="x", pady=(0, 8))
        tk.Label(qty_row, text="Qty", bg=self.colors["card"], fg=self.colors["muted"]).pack(side="left")
        self.pos_qty_entry = ttk.Entry(qty_row, textvariable=self.pos_qty_var, width=8)
        self.pos_qty_entry.pack(side="left", padx=8)
        ttk.Button(qty_row, text="Update Qty", style="Primary.TButton", command=self.update_cart_qty).pack(side="left")
        ttk.Button(qty_row, text="Remove", style="Danger.TButton", command=self.remove_cart_item).pack(side="left", padx=6)

        checkout_row = tk.Frame(right, bg=self.colors["card"])
        checkout_row.pack(fill="x")
        ttk.Button(checkout_row, text="Checkout", style="Success.TButton", command=self.checkout_pos).pack(side="left")
        ttk.Button(checkout_row, text="Print Receipt", style="Info.TButton", command=self.print_last_receipt).pack(side="left", padx=6)
        ttk.Button(checkout_row, text="Clear Cart", style="Danger.TButton", command=self.clear_cart).pack(side="left", padx=6)

        self.load_pos_items()
        self.load_quick_add_items()
    
    def create_bills_tab(self, notebook=None):
        """Create bills tab."""
        parent = notebook or self.notebook
        frame = ttk.Frame(parent)
        parent.add(frame, text="📋 Bills")
        if notebook is not None:
            self.crm_tab_index["Bills"] = frame
        else:
            self.tab_index["Bills"] = frame

        container = tk.Frame(frame, bg=self.colors["bg"])
        container.pack(fill="both", expand=True, padx=12, pady=12)

        header = tk.Frame(container, bg=self.colors["bg"])
        header.pack(fill="x", pady=(0, 12))
        ttk.Label(header, text="🧾 Bills Timeline", style="Header.TLabel").pack(side="left")
        ttk.Label(header, text="Recent sales history", style="Subheader.TLabel").pack(side="left", padx=10)

        # Scrollable timeline area
        canvas_frame = tk.Frame(container, bg=self.colors["bg"])
        canvas_frame.pack(fill="both", expand=True)

        self.bills_canvas = tk.Canvas(canvas_frame, bg=self.colors["bg"], highlightthickness=0)
        self.bills_scroll = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.bills_canvas.yview)
        self.bills_canvas.configure(yscrollcommand=self.bills_scroll.set)

        self.bills_scroll.pack(side="right", fill="y")
        self.bills_canvas.pack(side="left", fill="both", expand=True)

        self.bills_timeline_frame = tk.Frame(self.bills_canvas, bg=self.colors["bg"])
        self.bills_canvas_window = self.bills_canvas.create_window((0, 0), window=self.bills_timeline_frame, anchor="nw")

        self.bills_timeline_frame.bind(
            "<Configure>",
            lambda e: self.bills_canvas.configure(scrollregion=self.bills_canvas.bbox("all"))
        )
        self.bills_canvas.bind("<Configure>", self._resize_bills_canvas)

        self.refresh_bills_timeline()

    # === POS helpers ===
    def load_pos_items(self):
        """Load all inventory items into POS list."""
        for item in self.pos_items_tree.get_children():
            self.pos_items_tree.delete(item)

        items = self.inventory_service.get_all_items()
        for item in items:
            self.pos_items_tree.insert('', 'end', values=(item[0], item[1], CurrencyFormatter.format_currency(item[4])))

    def search_pos_items(self):
        """Search inventory for POS."""
        query = self.pos_search_entry.get().strip()
        for item in self.pos_items_tree.get_children():
            self.pos_items_tree.delete(item)

        items = self.inventory_service.search(query) if query else self.inventory_service.get_all_items()
        for item in items:
            self.pos_items_tree.insert('', 'end', values=(item[0], item[1], CurrencyFormatter.format_currency(item[4])))

    def load_quick_add_items(self):
        """Load quick add buttons based on top sales or inventory."""
        for widget in self.quick_add_frame.winfo_children():
            widget.destroy()

        start_date, end_date, _ = self.analytics_service.get_date_range("7")
        top_items = self.analytics_service.get_top_selling_items(start_date, end_date, limit=6)
        if not top_items:
            items = self.inventory_service.get_all_items()[:6]
            top_items = [(i[0], i[1], i[4]) for i in items]

        for idx, item in enumerate(top_items):
            name = item[0]
            btn = ttk.Button(self.quick_add_frame, text=name, style="Primary.TButton",
                             command=lambda n=name: self.add_item_by_name(n))
            btn.grid(row=idx // 3, column=idx % 3, padx=4, pady=4, sticky="ew")

    def add_item_by_name(self, item_name):
        """Add an item to the cart by name."""
        self.pos_selected_item = item_name
        self.add_selected_item_to_cart()

    def add_selected_item_to_cart(self, event=None):
        """Add selected item to cart."""
        if event is not None:
            selection = self.pos_items_tree.selection()
            if selection:
                values = self.pos_items_tree.item(selection[0])["values"]
                self.pos_selected_item = values[0]

        if not self.pos_selected_item:
            selection = self.pos_items_tree.selection()
            if selection:
                self.pos_selected_item = self.pos_items_tree.item(selection[0])["values"][0]

        if not self.pos_selected_item:
            messagebox.showerror("POS", "Select an item to add")
            return

        try:
            qty = int(self.pos_qty_var.get())
            if qty <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("POS", "Quantity must be a positive number")
            return

        item = self.inventory_service.get_item(self.pos_selected_item)
        if not item:
            messagebox.showerror("POS", "Item not found")
            return

        price = item.get("sale_price", 0)
        existing = next((i for i in self.pos_cart if i["item_name"] == self.pos_selected_item), None)
        if existing:
            existing["quantity"] += qty
        else:
            self.pos_cart.append({"item_name": self.pos_selected_item, "quantity": qty, "price": price})

        self.refresh_cart()

    def select_cart_item(self, event=None):
        """Select a cart item to update qty."""
        selection = self.pos_cart_tree.selection()
        if selection:
            values = self.pos_cart_tree.item(selection[0])["values"]
            self.pos_selected_item = values[0]
            self.pos_qty_var.set(str(values[1]))

    def update_cart_qty(self):
        """Update selected cart item quantity."""
        if not self.pos_selected_item:
            messagebox.showerror("POS", "Select a cart item")
            return
        try:
            qty = int(self.pos_qty_var.get())
            if qty <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("POS", "Quantity must be a positive number")
            return

        for item in self.pos_cart:
            if item["item_name"] == self.pos_selected_item:
                item["quantity"] = qty
                break
        self.refresh_cart()

    def remove_cart_item(self):
        """Remove selected cart item."""
        if not self.pos_selected_item:
            messagebox.showerror("POS", "Select a cart item")
            return
        messagebox.showwarning("Caution", "This will remove the selected item from the cart.")
        if not messagebox.askyesno("Confirm", "Remove the selected cart item?"):
            return
        self.pos_cart = [i for i in self.pos_cart if i["item_name"] != self.pos_selected_item]
        self.pos_selected_item = None
        self.refresh_cart()

    def clear_cart(self):
        """Clear POS cart."""
        messagebox.showwarning("Caution", "This will clear all items from the cart.")
        if not messagebox.askyesno("Confirm", "Clear the entire cart?"):
            return
        self.pos_cart = []
        self.pos_selected_item = None
        self.refresh_cart()

    def refresh_cart(self):
        """Refresh cart tree and total."""
        for item in self.pos_cart_tree.get_children():
            self.pos_cart_tree.delete(item)

        total = 0.0
        for item in self.pos_cart:
            line_total = item["quantity"] * item["price"]
            total += line_total
            self.pos_cart_tree.insert('', 'end', values=(
                item["item_name"], item["quantity"],
                CurrencyFormatter.format_currency(item["price"]),
                CurrencyFormatter.format_currency(line_total)
            ))

        self.pos_total_label.config(text=CurrencyFormatter.format_currency(total))

    def append_qty(self, digit: str):
        """Append a digit to qty entry."""
        current = self.pos_qty_var.get().strip()
        self.pos_qty_var.set((current + digit).lstrip("0") or "0")

    def clear_qty(self):
        """Clear quantity entry."""
        self.pos_qty_var.set("1")

    def checkout_pos(self):
        """Finalize sale and update inventory."""
        if not self.pos_cart:
            messagebox.showerror("POS", "Cart is empty")
            return

        sale_time = datetime.now()
        receipt_text = self._build_receipt_text(self.pos_cart, sale_time, self.current_user)
        self.last_receipt_text = receipt_text
        self.last_receipt_time = sale_time

        for item in self.pos_cart:
            name = item["item_name"]
            qty = item["quantity"]
            price = item["price"]

            self.pos_service.record_sale(name, qty, price, self.current_user)

            current = self.inventory_service.get_item(name)
            if current:
                new_qty = max(0, (current.get("quantity", 0) - qty))
                self.inventory_service.update_item(name, quantity=new_qty)

        self.activity_service.log(self.current_user, "POS Checkout", f"Processed {len(self.pos_cart)} items")
        self.clear_cart()
        self.load_pos_items()
        self.load_quick_add_items()
        messagebox.showinfo("POS", "Sale completed")

    def print_last_receipt(self):
        """Print the most recent POS receipt."""
        if not self.last_receipt_text:
            messagebox.showerror("POS", "No receipt to print. Checkout first.")
            return
        self._show_print_preview(self.last_receipt_text, "BzHub POS Receipt")

    def print_sale_receipt(self, sale_row):
        """Print a single sale from the Bills timeline."""
        receipt_text = self._build_single_sale_receipt(sale_row)
        self._show_print_preview(receipt_text, "BzHub Sale Receipt")

    def _build_receipt_text(self, items, sale_time, username):
        """Build a printable receipt for a cart."""
        info = self.company_service.get_info() or {}
        company_name = info.get("company_name") or "BzHub"
        address = info.get("address") or ""
        phone = info.get("phone") or ""
        email = info.get("email") or ""

        lines = []
        lines.append(company_name)
        if address:
            lines.append(address)
        contact = " · ".join([v for v in [phone, email] if v])
        if contact:
            lines.append(contact)
        lines.append("=" * 48)
        lines.append(f"Date: {sale_time.strftime('%Y-%m-%d %H:%M')}")
        if username:
            lines.append(f"User: {username}")
        lines.append("-" * 48)
        lines.append(f"{'Item':<24}{'Qty':>4}{'Price':>10}{'Total':>10}")
        lines.append("-" * 48)

        subtotal = 0.0
        for item in items:
            name = item["item_name"][:24]
            qty = item["quantity"]
            price = item["price"]
            total = qty * price
            subtotal += total
            lines.append(f"{name:<24}{qty:>4}{price:>10.2f}{total:>10.2f}")

        lines.append("-" * 48)
        lines.append(f"{'TOTAL':>38}{subtotal:>10.2f}")
        lines.append("=" * 48)
        lines.append("Thank you for your business!")
        return "\n".join(lines)

    def _build_single_sale_receipt(self, row):
        """Build a printable receipt for a single sale row."""
        _, sale_date, item_name, qty, sale_price, total_amount, username = row
        sale_time = str(sale_date)
        lines = []
        lines.append("BzHub Sale Receipt")
        lines.append("=" * 48)
        lines.append(f"Date: {sale_time}")
        if username:
            lines.append(f"User: {username}")
        lines.append("-" * 48)
        lines.append(f"Item: {item_name}")
        lines.append(f"Qty: {qty}")
        lines.append(f"Price: {sale_price:.2f}")
        lines.append(f"Total: {total_amount:.2f}")
        lines.append("=" * 48)
        return "\n".join(lines)

    def _print_text(self, text, job_name):
        """Send text to system printer (macOS/Linux)."""
        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as tmp:
                tmp.write(text)
                tmp_path = tmp.name

            subprocess.run(["lp", "-t", job_name, tmp_path], check=True)
            self.activity_service.log(self.current_user or "system", "Print", job_name)
            messagebox.showinfo("Print", "Sent to printer.")
        except Exception as e:
            messagebox.showerror("Print Error", f"Failed to print: {e}")

    def _show_print_preview(self, text, title):
        """Show a preview window before printing."""
        preview = tk.Toplevel(self.root)
        preview.title(title)
        preview.geometry("720x560")
        preview.minsize(640, 480)

        container = tk.Frame(preview, bg=self.colors["bg"], padx=12, pady=12)
        container.pack(fill="both", expand=True)

        tk.Label(container, text=title, bg=self.colors["bg"], fg=self.colors["text"],
                 font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 8))

        text_frame = tk.Frame(container, bg=self.colors["bg"])
        text_frame.pack(fill="both", expand=True)

        text_widget = tk.Text(text_frame, wrap="word", font=("Courier", 10))
        scroll = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scroll.set)
        text_widget.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        text_widget.insert("1.0", text)
        text_widget.config(state="disabled")

        actions = tk.Frame(container, bg=self.colors["bg"])
        actions.pack(fill="x", pady=(10, 0))
        ttk.Button(actions, text="Print", style="Success.TButton",
                   command=lambda: self._print_text(text, title)).pack(side="left")
        ttk.Button(actions, text="Close", style="Info.TButton",
                   command=preview.destroy).pack(side="right")

    def print_employee_id_card(self, row):
        """Print a simple employee ID card."""
        emp_id = row[0]
        emp_number = row[1] or "—"
        name = row[2] or "—"
        joining_date = row[3] or ""
        designation = row[4] or "—"
        manager = row[5] or "—"
        team = row[6] or "—"
        email = row[7] or "—"
        phone = row[8] or "—"
        emergency = row[9] or "—"

        expiry = HRCalculator.calculate_id_card_expiry(joining_date) if joining_date else ""
        info = self.company_service.get_info() or {}
        company_name = info.get("company_name") or "BzHub"

        lines = [
            company_name,
            "Employee ID Card",
            "=" * 40,
            f"Employee ID: {emp_number}",
            f"Name: {name}",
            f"Designation: {designation}",
            f"Team: {team}",
            f"Manager: {manager}",
            f"Email: {email}",
            f"Phone: {phone}",
            f"Emergency: {emergency}",
        ]
        if joining_date:
            lines.append(f"Joined: {joining_date}")
        if expiry:
            lines.append(f"Expires: {expiry}")
        lines.append("=" * 40)
        lines.append(f"Record ID: {emp_id}")

        self._show_print_preview("\n".join(lines), f"Employee ID Card - {emp_number}")
    
    def create_visitors_tab(self, notebook=None):
        """Create visitors tab."""
        parent = notebook or self.notebook
        frame = ttk.Frame(parent)
        parent.add(frame, text="👥 Visitors")
        if notebook is not None:
            self.crm_tab_index["Visitors"] = frame
        else:
            self.tab_index["Visitors"] = frame

        container = tk.Frame(frame, bg=self.colors["bg"])
        container.pack(fill="both", expand=True, padx=12, pady=12)

        header = tk.Frame(container, bg=self.colors["bg"])
        header.pack(fill="x", pady=(0, 12))
        ttk.Label(header, text="👥 Visitors", style="Header.TLabel").pack(side="left")
        ttk.Label(header, text="Contacts & visits", style="Subheader.TLabel").pack(side="left", padx=10)

        actions = tk.Frame(header, bg=self.colors["bg"])
        actions.pack(side="right")
        self.vis_search_var = tk.StringVar()
        self.vis_search_entry = ttk.Entry(actions, textvariable=self.vis_search_var, width=24)
        self.vis_search_entry.pack(side="left", padx=(0, 6))
        ttk.Button(actions, text="Search", style="Info.TButton", command=self.refresh_visitors_cards).pack(side="left", padx=4)
        ttk.Button(actions, text="Reset", style="Info.TButton", command=self.reset_visitors_search).pack(side="left")

        # Scrollable cards area
        canvas_frame = tk.Frame(container, bg=self.colors["bg"])
        canvas_frame.pack(fill="both", expand=True)

        self.vis_canvas = tk.Canvas(canvas_frame, bg=self.colors["bg"], highlightthickness=0)
        self.vis_scroll = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.vis_canvas.yview)
        self.vis_canvas.configure(yscrollcommand=self.vis_scroll.set)

        self.vis_scroll.pack(side="right", fill="y")
        self.vis_canvas.pack(side="left", fill="both", expand=True)

        self.vis_cards_frame = tk.Frame(self.vis_canvas, bg=self.colors["bg"])
        self.vis_canvas_window = self.vis_canvas.create_window((0, 0), window=self.vis_cards_frame, anchor="nw")

        self.vis_cards_frame.bind("<Configure>", lambda e: self.vis_canvas.configure(scrollregion=self.vis_canvas.bbox("all")))
        self.vis_canvas.bind("<Configure>", self._resize_vis_canvas)

        self.refresh_visitors_cards()
    
    def create_hr_tab(self):
        """Create HR tab (admin only)."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="👔 HR")
        self.tab_index["HR"] = frame

        container = tk.Frame(frame, bg=self.colors["bg"])
        container.pack(fill="both", expand=True, padx=12, pady=12)

        self.hr_notebook = ttk.Notebook(container)
        self.hr_notebook.pack(fill="both", expand=True)

        employees_tab = ttk.Frame(self.hr_notebook)
        payroll_tab = ttk.Frame(self.hr_notebook)
        appraisals_tab = ttk.Frame(self.hr_notebook)
        feedback_tab = ttk.Frame(self.hr_notebook)
        self.hr_notebook.add(employees_tab, text="Employees")
        self.hr_notebook.add(payroll_tab, text="Payroll")
        self.hr_notebook.add(appraisals_tab, text="Appraisals")
        self.hr_notebook.add(feedback_tab, text="Feedback")
        self.hr_tab_index = {
            "Employees": employees_tab,
            "Payroll": payroll_tab,
            "Appraisals": appraisals_tab,
            "Feedback": feedback_tab,
        }

        # === Employees tab ===
        container = tk.Frame(employees_tab, bg=self.colors["bg"])
        container.pack(fill="both", expand=True, padx=12, pady=12)

        header = tk.Frame(container, bg=self.colors["bg"])
        header.pack(fill="x", pady=(0, 12))
        ttk.Label(header, text="👔 HR", style="Header.TLabel").pack(side="left")
        ttk.Label(header, text="Employee profiles", style="Subheader.TLabel").pack(side="left", padx=10)

        actions = tk.Frame(header, bg=self.colors["bg"])
        actions.pack(side="right")
        ttk.Button(actions, text="Add Employee", style="Primary.TButton", command=self.open_add_employee_dialog).pack(side="left", padx=(0, 6))
        ttk.Button(actions, text="Payroll", style="Info.TButton",
                   command=lambda: self.hr_notebook.select(payroll_tab)).pack(side="left", padx=(0, 6))
        self.hr_search_var = tk.StringVar()
        self.hr_search_entry = ttk.Entry(actions, textvariable=self.hr_search_var, width=24)
        self.hr_search_entry.pack(side="left", padx=(0, 6))
        ttk.Button(actions, text="Search", style="Info.TButton", command=self.refresh_hr_cards).pack(side="left", padx=4)
        ttk.Button(actions, text="Reset", style="Info.TButton", command=self.reset_hr_search).pack(side="left")

        # Scrollable cards area
        canvas_frame = tk.Frame(container, bg=self.colors["bg"])
        canvas_frame.pack(fill="both", expand=True)

        self.hr_canvas = tk.Canvas(canvas_frame, bg=self.colors["bg"], highlightthickness=0)
        self.hr_scroll = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.hr_canvas.yview)
        self.hr_canvas.configure(yscrollcommand=self.hr_scroll.set)

        self.hr_scroll.pack(side="right", fill="y")
        self.hr_canvas.pack(side="left", fill="both", expand=True)

        self.hr_cards_frame = tk.Frame(self.hr_canvas, bg=self.colors["bg"])
        self.hr_canvas_window = self.hr_canvas.create_window((0, 0), window=self.hr_cards_frame, anchor="nw")

        self.hr_cards_frame.bind("<Configure>", lambda e: self.hr_canvas.configure(scrollregion=self.hr_canvas.bbox("all")))
        self.hr_canvas.bind("<Configure>", self._resize_hr_canvas)

        self.refresh_hr_cards()

        # === Payroll tab ===
        self.build_payroll_ui(payroll_tab)
        self.build_appraisals_ui(appraisals_tab)
        self.build_feedback_ui(feedback_tab)
    
    def create_reports_tab(self, notebook=None):
        """Create reports tab (admin only)."""
        parent = notebook or self.notebook
        frame = ttk.Frame(parent)
        parent.add(frame, text="📊 Reports")
        if notebook is not None:
            self.crm_tab_index["Reports"] = frame
        else:
            self.tab_index["Reports"] = frame

        container = tk.Frame(frame, bg=self.colors["bg"])
        container.pack(fill="both", expand=True, padx=12, pady=12)

        header = tk.Frame(container, bg=self.colors["bg"])
        header.pack(fill="x", pady=(0, 12))
        ttk.Label(header, text="📈 Reports", style="Header.TLabel").pack(side="left")
        ttk.Label(header, text="Sales insights and performance", style="Subheader.TLabel").pack(side="left", padx=10)

        period_frame = tk.Frame(header, bg=self.colors["bg"])
        period_frame.pack(side="right")
        ttk.Label(period_frame, text="Time Range", style="Subheader.TLabel").pack(side="left", padx=(0, 8))

        self.reports_period_var = tk.StringVar(value="Last 30 Days")
        self.reports_period_map = {
            "Last 7 Days": "7",
            "Last 30 Days": "30",
            "Quarter": "90",
            "Year": "365",
        }
        self.reports_period_combo = ttk.Combobox(period_frame, values=list(self.reports_period_map.keys()),
                                                 textvariable=self.reports_period_var, state="readonly", width=16)
        self.reports_period_combo.pack(side="left")
        self.reports_period_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_reports())

        # Summary cards
        cards_row = tk.Frame(container, bg=self.colors["bg"])
        cards_row.pack(fill="x", pady=(0, 12))

        self.reports_kpi = {}
        self.reports_kpi["total_sales"] = self._create_kpi_card(cards_row, "Total Sales")
        self.reports_kpi["avg_daily"] = self._create_kpi_card(cards_row, "Avg Daily Sales")
        self.reports_kpi["top_item"] = self._create_kpi_card(cards_row, "Top Item")
        self.reports_kpi["items_sold"] = self._create_kpi_card(cards_row, "Items Sold")

        # Charts
        charts_row = tk.Frame(container, bg=self.colors["bg"])
        charts_row.pack(fill="both", expand=True)

        trend_card = tk.Frame(charts_row, bg=self.colors["card"], padx=12, pady=12)
        trend_card.pack(side="left", fill="both", expand=True, padx=(0, 8))
        tk.Label(trend_card, text="Sales Trend", bg=self.colors["card"], fg=self.colors["text"],
                 font=("Arial", 10, "bold")).pack(anchor="w")

        self.reports_sales_fig = Figure(figsize=(5, 3), dpi=100)
        self.reports_sales_ax = self.reports_sales_fig.add_subplot(111)
        self.reports_sales_canvas = FigureCanvasTkAgg(self.reports_sales_fig, master=trend_card)
        self.reports_sales_canvas.get_tk_widget().pack(fill="both", expand=True)
        self.reports_sales_canvas.get_tk_widget().bind(
            "<Configure>",
            lambda e: self._resize_figure(e, self.reports_sales_fig, self.reports_sales_canvas)
        )
        self.reports_sales_canvas.get_tk_widget().bind(
            "<Double-1>",
            lambda _e: self.open_chart_zoom("Sales Trend", lambda ax: self._draw_sales_trend(ax, self._reports_trend))
        )

        items_card = tk.Frame(charts_row, bg=self.colors["card"], padx=12, pady=12)
        items_card.pack(side="left", fill="both", expand=True, padx=(8, 0))
        tk.Label(items_card, text="Top Items", bg=self.colors["card"], fg=self.colors["text"],
                 font=("Arial", 10, "bold")).pack(anchor="w")

        self.reports_items_fig = Figure(figsize=(5, 3), dpi=100)
        self.reports_items_ax = self.reports_items_fig.add_subplot(111)
        self.reports_items_canvas = FigureCanvasTkAgg(self.reports_items_fig, master=items_card)
        self.reports_items_canvas.get_tk_widget().pack(fill="both", expand=True)
        self.reports_items_canvas.get_tk_widget().bind(
            "<Configure>",
            lambda e: self._resize_figure(e, self.reports_items_fig, self.reports_items_canvas)
        )
        self.reports_items_canvas.get_tk_widget().bind(
            "<Double-1>",
            lambda _e: self.open_chart_zoom("Top Items", lambda ax: self._draw_top_items(ax, self._reports_summary))
        )

        self.refresh_reports()
    
    def create_settings_tab(self):
        """Create settings tab (admin only)."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="⚙️ Settings")
        self.tab_index["Settings"] = frame

        container = tk.Frame(frame, bg=self.colors["bg"])
        container.pack(fill="both", expand=True, padx=12, pady=12)

        header = tk.Frame(container, bg=self.colors["bg"])
        header.pack(fill="x", pady=(0, 12))
        ttk.Label(header, text="⚙️ Settings", style="Header.TLabel").pack(side="left")
        ttk.Label(header, text="Company & Email configuration", style="Subheader.TLabel").pack(side="left", padx=10)

        body = tk.Frame(container, bg=self.colors["bg"])
        body.pack(fill="both", expand=True)

        # Company Info Card
        company_card = tk.Frame(body, bg=self.colors["card"], padx=12, pady=12)
        company_card.pack(side="left", fill="both", expand=True, padx=(0, 8))

        title_row = tk.Frame(company_card, bg=self.colors["card"])
        title_row.pack(fill="x")
        tk.Label(title_row, text="Company Info", bg=self.colors["card"], fg=self.colors["text"],
                 font=("Arial", 10, "bold")).pack(side="left")
        self.company_lock_status = tk.Label(title_row, text="", bg=self.colors["card"], fg=self.colors["muted"], font=("Arial", 9))
        self.company_lock_status.pack(side="right")

        def company_field(label_text):
            row = tk.Frame(company_card, bg=self.colors["card"])
            row.pack(fill="x", pady=4)
            tk.Label(row, text=label_text, bg=self.colors["card"], fg=self.colors["muted"], width=14, anchor="w").pack(side="left")
            entry = ttk.Entry(row)
            entry.pack(side="left", fill="x", expand=True)
            return entry

        self.company_name_entry = company_field("Name")
        self.company_address_entry = company_field("Address")
        self.company_phone_entry = company_field("Phone")
        self.company_email_entry = company_field("Email")
        self.company_tax_entry = company_field("Tax ID")
        self.company_bank_entry = company_field("Bank Details")

        company_btn_row = tk.Frame(company_card, bg=self.colors["card"])
        company_btn_row.pack(fill="x", pady=(8, 0))
        ttk.Button(company_btn_row, text="Save", style="Success.TButton", command=self.save_company_info).pack(side="left")
        ttk.Button(company_btn_row, text="Unlock", style="Info.TButton", command=self.unlock_company_info).pack(side="left", padx=6)

        # Email Config Card
        email_card = tk.Frame(body, bg=self.colors["card"], padx=12, pady=12)
        email_card.pack(side="left", fill="both", expand=True, padx=(8, 0))

        tk.Label(email_card, text="Email Settings", bg=self.colors["card"], fg=self.colors["text"],
                 font=("Arial", 10, "bold")).pack(anchor="w")

        def email_field(label_text, show=None):
            row = tk.Frame(email_card, bg=self.colors["card"])
            row.pack(fill="x", pady=4)
            tk.Label(row, text=label_text, bg=self.colors["card"], fg=self.colors["muted"], width=14, anchor="w").pack(side="left")
            entry = ttk.Entry(row, show=show) if show else ttk.Entry(row)
            entry.pack(side="left", fill="x", expand=True)
            return entry

        self.smtp_server_entry = email_field("SMTP Server")
        self.smtp_port_entry = email_field("SMTP Port")
        self.sender_email_entry = email_field("Sender Email")
        self.sender_password_entry = email_field("Password", show="*")
        self.recipient_email_entry = email_field("Recipient")

        email_btn_row = tk.Frame(email_card, bg=self.colors["card"])
        email_btn_row.pack(fill="x", pady=(8, 0))
        ttk.Button(email_btn_row, text="Save", style="Success.TButton", command=self.save_email_config).pack(side="left")
        ttk.Button(email_btn_row, text="Test", style="Info.TButton", command=self.test_email_config).pack(side="left", padx=6)

        self.load_company_info()
        self.load_email_config()

    # === HR helpers ===
    def _resize_hr_canvas(self, event):
        """Resize HR canvas to match container width."""
        self.hr_canvas.itemconfig(self.hr_canvas_window, width=event.width)

    def open_add_employee_dialog(self):
        """Open dialog to add a new employee."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Employee")
        dialog.geometry("460x560")
        dialog.minsize(420, 520)

        container = tk.Frame(dialog, bg=self.colors["bg"], padx=12, pady=12)
        container.pack(fill="both", expand=True)

        tk.Label(container, text="Add Employee", bg=self.colors["bg"], fg=self.colors["text"],
                 font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 8))

        def field(label_text):
            row = tk.Frame(container, bg=self.colors["bg"])
            row.pack(fill="x", pady=4)
            tk.Label(row, text=label_text, bg=self.colors["bg"], fg=self.colors["muted"], width=14, anchor="w").pack(side="left")
            entry = ttk.Entry(row)
            entry.pack(side="left", fill="x", expand=True)
            return entry

        emp_number = field("Emp Number")
        name = field("Name")
        joining = field("Joining Date")
        designation = field("Designation")
        manager = field("Manager")
        team = field("Team")
        email = field("Email")
        phone = field("Phone")
        emergency = field("Emergency")
        notes = field("Notes")

        btn_row = tk.Frame(container, bg=self.colors["bg"])
        btn_row.pack(fill="x", pady=(10, 0))

        def save_employee():
            try:
                if self.hr_service.add_employee(
                    emp_number.get().strip(),
                    name.get().strip(),
                    joining.get().strip(),
                    designation.get().strip(),
                    manager.get().strip(),
                    team.get().strip(),
                    email.get().strip(),
                    phone.get().strip(),
                    emergency.get().strip(),
                    "",
                    notes.get().strip(),
                    1,
                ):
                    self.activity_service.log(self.current_user, "Add Employee", f"Added employee: {name.get().strip()}")
                    self.refresh_hr_cards()
                    dialog.destroy()
                else:
                    messagebox.showerror("HR", "Failed to add employee")
            except Exception as e:
                messagebox.showerror("HR", f"Invalid input: {e}")

        ttk.Button(btn_row, text="Save", style="Success.TButton", command=save_employee).pack(side="left")
        ttk.Button(btn_row, text="Cancel", style="Info.TButton", command=dialog.destroy).pack(side="right")

    def open_payroll_manager(self):
        """Open payroll manager window."""
        window = tk.Toplevel(self.root)
        window.title("Payroll Manager")
        window.geometry("900x600")
        window.minsize(820, 540)
        self.build_payroll_ui(window)

    def build_payroll_ui(self, parent):
        """Build payroll UI inside a parent container."""
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

        def form_field(label_text):
            row = tk.Frame(form_card, bg=self.colors["card"])
            row.pack(fill="x", pady=4)
            tk.Label(row, text=label_text, bg=self.colors["card"], fg=self.colors["muted"], width=14, anchor="w").pack(side="left")
            entry = ttk.Entry(row)
            entry.pack(side="left", fill="x", expand=True)
            return entry

        # Employees
        employees = self.hr_service.get_all_employees()
        active_emps = [e for e in employees if len(e) > 12 and e[12] == 1]
        emp_options = [f"{e[0]} - {e[2]}" for e in active_emps]
        emp_row = tk.Frame(form_card, bg=self.colors["card"])
        emp_row.pack(fill="x", pady=4)
        tk.Label(emp_row, text="Employee", bg=self.colors["card"], fg=self.colors["muted"], width=14, anchor="w").pack(side="left")
        emp_var = tk.StringVar()
        emp_combo = ttk.Combobox(emp_row, values=emp_options, textvariable=emp_var, state="readonly")
        emp_combo.pack(side="left", fill="x", expand=True)

        period_start = form_field("Period Start")
        period_end = form_field("Period End")
        base_salary = form_field("Base Salary")
        allowances = form_field("Allowances")
        deductions = form_field("Deductions")
        overtime_hours = form_field("Overtime Hours")
        overtime_rate = form_field("Overtime Rate")
        status = form_field("Status")
        paid_date = form_field("Paid Date")

        status.insert(0, "Draft")

        columns = ("ID", "Employee", "Period", "Gross", "Net", "Status", "Paid")
        payroll_tree = ttk.Treeview(list_card, columns=columns, show="headings", height=14)
        for col, width in [("ID", 60), ("Employee", 180), ("Period", 160), ("Gross", 90), ("Net", 90), ("Status", 90), ("Paid", 120)]:
            payroll_tree.column(col, anchor="center", width=width)
            payroll_tree.heading(col, text=col)
        payroll_tree.pack(fill="both", expand=True)

        def parse_employee_id():
            if not emp_var.get():
                return None
            return int(emp_var.get().split(" - ", 1)[0])

        def refresh_payroll_list():
            for item in payroll_tree.get_children():
                payroll_tree.delete(item)
            rows = self.payroll_service.get_all_payrolls()
            emp_lookup = {e[0]: e[2] for e in employees}
            for row in rows:
                payroll_id = row[0]
                employee_id = row[1]
                period = f"{row[2]} → {row[3]}"
                gross = CurrencyFormatter.format_currency(row[9])
                net = CurrencyFormatter.format_currency(row[10])
                payroll_tree.insert('', 'end', values=(
                    payroll_id,
                    emp_lookup.get(employee_id, str(employee_id)),
                    period,
                    gross,
                    net,
                    row[11],
                    row[12] or ""
                ))

        def clear_form():
            emp_var.set("")
            for entry in [period_start, period_end, base_salary, allowances, deductions, overtime_hours, overtime_rate, status, paid_date]:
                entry.delete(0, tk.END)
            status.insert(0, "Draft")

        def add_payroll():
            try:
                emp_id = parse_employee_id()
                if not emp_id:
                    messagebox.showerror("Payroll", "Select an employee")
                    return
                if self.payroll_service.add_payroll(
                    emp_id,
                    period_start.get().strip(),
                    period_end.get().strip(),
                    float(base_salary.get() or 0),
                    float(allowances.get() or 0),
                    float(deductions.get() or 0),
                    float(overtime_hours.get() or 0),
                    float(overtime_rate.get() or 0),
                    status.get().strip() or "Draft",
                    paid_date.get().strip(),
                ):
                    refresh_payroll_list()
                    clear_form()
                else:
                    messagebox.showerror("Payroll", "Failed to add payroll")
            except Exception as e:
                messagebox.showerror("Payroll", f"Invalid input: {e}")

        def update_payroll():
            selection = payroll_tree.selection()
            if not selection:
                messagebox.showerror("Payroll", "Select a payroll record")
                return
            payroll_id = payroll_tree.item(selection[0])["values"][0]
            try:
                emp_id = parse_employee_id()
                self.payroll_service.update_payroll(
                    int(payroll_id),
                    employee_id=emp_id,
                    period_start=period_start.get().strip(),
                    period_end=period_end.get().strip(),
                    base_salary=float(base_salary.get() or 0),
                    allowances=float(allowances.get() or 0),
                    deductions=float(deductions.get() or 0),
                    overtime_hours=float(overtime_hours.get() or 0),
                    overtime_rate=float(overtime_rate.get() or 0),
                    status=status.get().strip() or "Draft",
                    paid_date=paid_date.get().strip(),
                )
                refresh_payroll_list()
            except Exception as e:
                messagebox.showerror("Payroll", f"Invalid input: {e}")

        def delete_payroll():
            selection = payroll_tree.selection()
            if not selection:
                messagebox.showerror("Payroll", "Select a payroll record")
                return
            payroll_id = payroll_tree.item(selection[0])["values"][0]
            messagebox.showwarning("Caution", "This will permanently delete the payroll record.")
            if not messagebox.askyesno("Confirm", "Delete the selected payroll record?"):
                return
            if self.payroll_service.delete_payroll(int(payroll_id)):
                refresh_payroll_list()
            else:
                messagebox.showerror("Payroll", "Failed to delete payroll")

        def on_select(event=None):
            selection = payroll_tree.selection()
            if not selection:
                return
            values = payroll_tree.item(selection[0])["values"]
            payroll_id = values[0]
            record = next((r for r in self.payroll_service.get_all_payrolls() if r[0] == payroll_id), None)
            if not record:
                return
            emp_var.set(f"{record[1]} - {next((e[2] for e in employees if e[0] == record[1]), record[1])}")
            period_start.delete(0, tk.END)
            period_start.insert(0, record[2] or "")
            period_end.delete(0, tk.END)
            period_end.insert(0, record[3] or "")
            base_salary.delete(0, tk.END)
            base_salary.insert(0, record[4] or 0)
            allowances.delete(0, tk.END)
            allowances.insert(0, record[5] or 0)
            deductions.delete(0, tk.END)
            deductions.insert(0, record[6] or 0)
            overtime_hours.delete(0, tk.END)
            overtime_hours.insert(0, record[7] or 0)
            overtime_rate.delete(0, tk.END)
            overtime_rate.insert(0, record[8] or 0)
            status.delete(0, tk.END)
            status.insert(0, record[11] or "Draft")
            paid_date.delete(0, tk.END)
            paid_date.insert(0, record[12] or "")

        payroll_tree.bind("<Double-1>", on_select)

        btn_row = tk.Frame(form_card, bg=self.colors["card"])
        btn_row.pack(fill="x", pady=(10, 0))
        ttk.Button(btn_row, text="Add", style="Success.TButton", command=add_payroll).pack(side="left", padx=3)
        ttk.Button(btn_row, text="Update", style="Primary.TButton", command=update_payroll).pack(side="left", padx=3)
        ttk.Button(btn_row, text="Delete", style="Danger.TButton", command=delete_payroll).pack(side="left", padx=3)
        ttk.Button(btn_row, text="Clear", style="Info.TButton", command=clear_form).pack(side="left", padx=3)

        refresh_payroll_list()

    def build_appraisals_ui(self, parent):
        """Build appraisals workflow UI."""
        container = tk.Frame(parent, bg=self.colors["bg"], padx=12, pady=12)
        container.pack(fill="both", expand=True)

        header = tk.Frame(container, bg=self.colors["bg"])
        header.pack(fill="x", pady=(0, 8))
        tk.Label(header, text="Appraisals", bg=self.colors["bg"], fg=self.colors["text"],
                 font=("Arial", 12, "bold")).pack(side="left")

        body = tk.Frame(container, bg=self.colors["bg"])
        body.pack(fill="both", expand=True)

        form_card = tk.Frame(body, bg=self.colors["card"], padx=12, pady=12)
        form_card.pack(side="left", fill="y", padx=(0, 10))

        list_card = tk.Frame(body, bg=self.colors["card"], padx=12, pady=12)
        list_card.pack(side="left", fill="both", expand=True)

        def form_field(label_text):
            row = tk.Frame(form_card, bg=self.colors["card"])
            row.pack(fill="x", pady=4)
            tk.Label(row, text=label_text, bg=self.colors["card"], fg=self.colors["muted"], width=14, anchor="w").pack(side="left")
            entry = ttk.Entry(row)
            entry.pack(side="left", fill="x", expand=True)
            return entry

        employees = self.hr_service.get_all_employees()
        emp_options = [f"{e[0]} - {e[2]}" for e in employees]
        emp_row = tk.Frame(form_card, bg=self.colors["card"])
        emp_row.pack(fill="x", pady=4)
        tk.Label(emp_row, text="Employee", bg=self.colors["card"], fg=self.colors["muted"], width=14, anchor="w").pack(side="left")
        emp_var = tk.StringVar()
        emp_combo = ttk.Combobox(emp_row, values=emp_options, textvariable=emp_var, state="readonly")
        emp_combo.pack(side="left", fill="x", expand=True)

        period_start = form_field("Period Start")
        period_end = form_field("Period End")

        self_text = tk.Text(form_card, height=4)
        tk.Label(form_card, text="Self Appraisal", bg=self.colors["card"], fg=self.colors["muted"]).pack(anchor="w", pady=(8, 0))
        self_text.pack(fill="x", pady=(2, 6))
        self_rating = form_field("Self Rating")

        manager_text = tk.Text(form_card, height=4)
        tk.Label(form_card, text="Manager Review", bg=self.colors["card"], fg=self.colors["muted"]).pack(anchor="w", pady=(8, 0))
        manager_text.pack(fill="x", pady=(2, 6))
        manager_rating = form_field("Manager Rating")
        final_rating = form_field("Final Rating")

        columns = ("ID", "Employee", "Period", "Status", "Final")
        tree = ttk.Treeview(list_card, columns=columns, show="headings", height=14)
        for col, width in [("ID", 60), ("Employee", 180), ("Period", 160), ("Status", 120), ("Final", 90)]:
            tree.column(col, anchor="center", width=width)
            tree.heading(col, text=col)
        tree.pack(fill="both", expand=True)

        def parse_employee_id():
            if not emp_var.get():
                return None
            return int(emp_var.get().split(" - ", 1)[0])

        def refresh_list():
            for item in tree.get_children():
                tree.delete(item)
            rows = self.appraisal_service.get_all_appraisals()
            emp_lookup = {e[0]: e[2] for e in employees}
            for row in rows:
                appraisal_id = row[0]
                employee_id = row[1]
                period = f"{row[2]} → {row[3]}"
                tree.insert('', 'end', values=(
                    appraisal_id,
                    emp_lookup.get(employee_id, str(employee_id)),
                    period,
                    row[4],
                    row[9] if row[9] is not None else ""
                ))

        def clear_form():
            emp_var.set("")
            for entry in [period_start, period_end, self_rating, manager_rating, final_rating]:
                entry.delete(0, tk.END)
            self_text.delete("1.0", tk.END)
            manager_text.delete("1.0", tk.END)

        def create_appraisal():
            emp_id = parse_employee_id()
            if not emp_id:
                messagebox.showerror("Appraisals", "Select an employee")
                return
            if self.appraisal_service.create_appraisal(emp_id, period_start.get().strip(), period_end.get().strip(), self.current_user or ""):
                refresh_list()
                clear_form()
            else:
                messagebox.showerror("Appraisals", "Failed to create appraisal")

        def submit_self():
            selection = tree.selection()
            if not selection:
                messagebox.showerror("Appraisals", "Select an appraisal")
                return
            appraisal_id = tree.item(selection[0])["values"][0]
            try:
                rating = float(self_rating.get() or 0)
            except Exception:
                rating = 0
            self.appraisal_service.update_self_appraisal(int(appraisal_id), self_text.get("1.0", tk.END).strip(), rating)
            refresh_list()

        def submit_manager():
            selection = tree.selection()
            if not selection:
                messagebox.showerror("Appraisals", "Select an appraisal")
                return
            appraisal_id = tree.item(selection[0])["values"][0]
            try:
                rating = float(manager_rating.get() or 0)
            except Exception:
                rating = 0
            self.appraisal_service.update_manager_review(int(appraisal_id), manager_text.get("1.0", tk.END).strip(), rating)
            refresh_list()

        def finalize():
            selection = tree.selection()
            if not selection:
                messagebox.showerror("Appraisals", "Select an appraisal")
                return
            appraisal_id = tree.item(selection[0])["values"][0]
            try:
                rating = float(final_rating.get() or 0)
            except Exception:
                rating = 0
            self.appraisal_service.finalize_appraisal(int(appraisal_id), rating)
            refresh_list()

        def on_select(event=None):
            selection = tree.selection()
            if not selection:
                return
            appraisal_id = int(tree.item(selection[0])["values"][0])
            record = next((r for r in self.appraisal_service.get_all_appraisals() if r[0] == appraisal_id), None)
            if not record:
                return
            emp_var.set(f"{record[1]} - {next((e[2] for e in employees if e[0] == record[1]), record[1])}")
            period_start.delete(0, tk.END)
            period_start.insert(0, record[2] or "")
            period_end.delete(0, tk.END)
            period_end.insert(0, record[3] or "")
            self_text.delete("1.0", tk.END)
            self_text.insert("1.0", record[5] or "")
            self_rating.delete(0, tk.END)
            self_rating.insert(0, record[6] or "")
            manager_text.delete("1.0", tk.END)
            manager_text.insert("1.0", record[7] or "")
            manager_rating.delete(0, tk.END)
            manager_rating.insert(0, record[8] or "")
            final_rating.delete(0, tk.END)
            final_rating.insert(0, record[9] or "")

        tree.bind("<Double-1>", on_select)

        btn_row = tk.Frame(form_card, bg=self.colors["card"])
        btn_row.pack(fill="x", pady=(10, 0))
        ttk.Button(btn_row, text="Create", style="Success.TButton", command=create_appraisal).pack(side="left", padx=3)
        ttk.Button(btn_row, text="Self Submit", style="Primary.TButton", command=submit_self).pack(side="left", padx=3)
        ttk.Button(btn_row, text="Manager Review", style="Info.TButton", command=submit_manager).pack(side="left", padx=3)
        ttk.Button(btn_row, text="Finalize", style="Danger.TButton", command=finalize).pack(side="left", padx=3)
        ttk.Button(btn_row, text="Clear", style="Info.TButton", command=clear_form).pack(side="left", padx=3)

        refresh_list()

    def build_feedback_ui(self, parent):
        """Build 360 feedback UI."""
        container = tk.Frame(parent, bg=self.colors["bg"], padx=12, pady=12)
        container.pack(fill="both", expand=True)

        header = tk.Frame(container, bg=self.colors["bg"])
        header.pack(fill="x", pady=(0, 8))
        tk.Label(header, text="360 Feedback", bg=self.colors["bg"], fg=self.colors["text"],
                 font=("Arial", 12, "bold")).pack(side="left")

        body = tk.Frame(container, bg=self.colors["bg"])
        body.pack(fill="both", expand=True)

        form_card = tk.Frame(body, bg=self.colors["card"], padx=12, pady=12)
        form_card.pack(side="left", fill="y", padx=(0, 10))

        list_card = tk.Frame(body, bg=self.colors["card"], padx=12, pady=12)
        list_card.pack(side="left", fill="both", expand=True)

        employees = self.hr_service.get_all_employees()
        emp_options = [f"{e[0]} - {e[2]}" for e in employees]
        appraisals = self.appraisal_service.get_all_appraisals()
        appraisal_options = [f"{a[0]} - {a[1]}" for a in appraisals]

        def row_label(parent_row, label_text):
            tk.Label(parent_row, text=label_text, bg=self.colors["card"], fg=self.colors["muted"], width=14, anchor="w").pack(side="left")

        # Request feedback
        tk.Label(form_card, text="Request Feedback", bg=self.colors["card"], fg=self.colors["text"],
                 font=("Arial", 10, "bold")).pack(anchor="w")

        req_row = tk.Frame(form_card, bg=self.colors["card"])
        req_row.pack(fill="x", pady=4)
        row_label(req_row, "Target")
        req_target = tk.StringVar()
        req_target_combo = ttk.Combobox(req_row, values=emp_options, textvariable=req_target, state="readonly")
        req_target_combo.pack(side="left", fill="x", expand=True)

        req_app_row = tk.Frame(form_card, bg=self.colors["card"])
        req_app_row.pack(fill="x", pady=4)
        row_label(req_app_row, "Appraisal")
        req_app = tk.StringVar()
        req_app_combo = ttk.Combobox(req_app_row, values=appraisal_options, textvariable=req_app, state="readonly")
        req_app_combo.pack(side="left", fill="x", expand=True)

        req_msg = tk.Text(form_card, height=3)
        tk.Label(form_card, text="Message", bg=self.colors["card"], fg=self.colors["muted"]).pack(anchor="w", pady=(6, 0))
        req_msg.pack(fill="x", pady=(2, 6))

        # Add feedback
        tk.Label(form_card, text="Give Feedback", bg=self.colors["card"], fg=self.colors["text"],
                 font=("Arial", 10, "bold")).pack(anchor="w", pady=(8, 0))

        from_row = tk.Frame(form_card, bg=self.colors["card"])
        from_row.pack(fill="x", pady=4)
        row_label(from_row, "From")
        fb_from = tk.StringVar()
        fb_from_combo = ttk.Combobox(from_row, values=emp_options, textvariable=fb_from, state="readonly")
        fb_from_combo.pack(side="left", fill="x", expand=True)

        to_row = tk.Frame(form_card, bg=self.colors["card"])
        to_row.pack(fill="x", pady=4)
        row_label(to_row, "To")
        fb_to = tk.StringVar()
        fb_to_combo = ttk.Combobox(to_row, values=emp_options, textvariable=fb_to, state="readonly")
        fb_to_combo.pack(side="left", fill="x", expand=True)

        fb_app_row = tk.Frame(form_card, bg=self.colors["card"])
        fb_app_row.pack(fill="x", pady=4)
        row_label(fb_app_row, "Appraisal")
        fb_app = tk.StringVar()
        fb_app_combo = ttk.Combobox(fb_app_row, values=appraisal_options, textvariable=fb_app, state="readonly")
        fb_app_combo.pack(side="left", fill="x", expand=True)

        rating_row = tk.Frame(form_card, bg=self.colors["card"])
        rating_row.pack(fill="x", pady=4)
        row_label(rating_row, "Rating")
        fb_rating = ttk.Entry(rating_row)
        fb_rating.pack(side="left", fill="x", expand=True)

        fb_text = tk.Text(form_card, height=3)
        tk.Label(form_card, text="Feedback", bg=self.colors["card"], fg=self.colors["muted"]).pack(anchor="w", pady=(6, 0))
        fb_text.pack(fill="x", pady=(2, 6))

        # Lists
        list_tabs = ttk.Notebook(list_card)
        list_tabs.pack(fill="both", expand=True)
        req_list_tab = ttk.Frame(list_tabs)
        fb_list_tab = ttk.Frame(list_tabs)
        list_tabs.add(req_list_tab, text="Requests")
        list_tabs.add(fb_list_tab, text="Entries")

        req_tree = ttk.Treeview(req_list_tab, columns=("ID", "Target", "Status", "Message"), show="headings", height=10)
        for col, width in [("ID", 60), ("Target", 160), ("Status", 90), ("Message", 240)]:
            req_tree.column(col, anchor="center", width=width)
            req_tree.heading(col, text=col)
        req_tree.pack(fill="both", expand=True)

        fb_tree = ttk.Treeview(fb_list_tab, columns=("ID", "From", "To", "Rating", "Feedback"), show="headings", height=10)
        for col, width in [("ID", 60), ("From", 140), ("To", 140), ("Rating", 80), ("Feedback", 240)]:
            fb_tree.column(col, anchor="center", width=width)
            fb_tree.heading(col, text=col)
        fb_tree.pack(fill="both", expand=True)

        def parse_emp_id(value):
            if not value:
                return None
            return int(value.split(" - ", 1)[0])

        def parse_appraisal_id(value):
            if not value:
                return None
            return int(value.split(" - ", 1)[0])

        def refresh_requests():
            for item in req_tree.get_children():
                req_tree.delete(item)
            rows = self.appraisal_service.get_feedback_requests()
            emp_lookup = {e[0]: e[2] for e in employees}
            for row in rows:
                req_tree.insert('', 'end', values=(
                    row[0],
                    emp_lookup.get(row[3], str(row[3])),
                    row[5],
                    (row[4] or "")[:60]
                ))

        def refresh_entries():
            for item in fb_tree.get_children():
                fb_tree.delete(item)
            rows = self.appraisal_service.get_feedback_entries()
            emp_lookup = {e[0]: e[2] for e in employees}
            for row in rows:
                fb_tree.insert('', 'end', values=(
                    row[0],
                    emp_lookup.get(row[2], str(row[2])),
                    emp_lookup.get(row[3], str(row[3])),
                    row[4] if row[4] is not None else "",
                    (row[5] or "")[:60]
                ))

        def add_request():
            target_id = parse_emp_id(req_target.get())
            if not target_id:
                messagebox.showerror("Feedback", "Select target employee")
                return
            appraisal_id = parse_appraisal_id(req_app.get())
            if self.appraisal_service.create_feedback_request(appraisal_id, self.current_user or "", target_id, req_msg.get("1.0", tk.END).strip()):
                req_msg.delete("1.0", tk.END)
                refresh_requests()
            else:
                messagebox.showerror("Feedback", "Failed to create request")

        def add_feedback():
            from_id = parse_emp_id(fb_from.get())
            to_id = parse_emp_id(fb_to.get())
            if not from_id or not to_id:
                messagebox.showerror("Feedback", "Select From and To employees")
                return
            appraisal_id = parse_appraisal_id(fb_app.get())
            try:
                rating = float(fb_rating.get() or 0)
            except Exception:
                rating = 0
            if self.appraisal_service.add_feedback_entry(appraisal_id, from_id, to_id, rating, fb_text.get("1.0", tk.END).strip()):
                fb_text.delete("1.0", tk.END)
                fb_rating.delete(0, tk.END)
                refresh_entries()
            else:
                messagebox.showerror("Feedback", "Failed to add feedback")

        btn_row = tk.Frame(form_card, bg=self.colors["card"])
        btn_row.pack(fill="x", pady=(8, 0))
        ttk.Button(btn_row, text="Request", style="Primary.TButton", command=add_request).pack(side="left", padx=3)
        ttk.Button(btn_row, text="Add Feedback", style="Success.TButton", command=add_feedback).pack(side="left", padx=3)

        refresh_requests()
        refresh_entries()

    def reset_hr_search(self):
        """Reset HR search field and refresh cards."""
        self.hr_search_var.set("")
        self.refresh_hr_cards()

    def refresh_hr_cards(self):
        """Refresh employee profile cards."""
        for widget in self.hr_cards_frame.winfo_children():
            widget.destroy()

        query = (self.hr_search_var.get() or "").strip().lower()
        employees = self.hr_service.get_all_employees()

        filtered = []
        for row in employees:
            emp_number = row[1] or ""
            name = row[2] or ""
            designation = row[4] or ""
            team = row[6] or ""
            email = row[7] or ""
            if not query or any(query in str(v).lower() for v in [emp_number, name, designation, team, email]):
                filtered.append(row)

        if not filtered:
            empty = tk.Frame(self.hr_cards_frame, bg=self.colors["card"], padx=12, pady=12)
            empty.pack(fill="x", pady=6)
            tk.Label(empty, text="No employees found", bg=self.colors["card"], fg=self.colors["muted"]).pack(anchor="w")
            return

        # Card grid (2 columns)
        for idx, row in enumerate(filtered):
            card = self._create_employee_card(self.hr_cards_frame, row)
            r = idx // 2
            c = idx % 2
            card.grid(row=r, column=c, padx=6, pady=6, sticky="nsew")

        self.hr_cards_frame.grid_columnconfigure(0, weight=1)
        self.hr_cards_frame.grid_columnconfigure(1, weight=1)

    def _create_employee_card(self, parent, row):
        """Build a single employee profile card."""
        emp_id = row[0]
        emp_number = row[1] or "—"
        name = row[2] or "—"
        joining_date = row[3] or "—"
        designation = row[4] or "—"
        manager = row[5] or "—"
        team = row[6] or "—"
        email = row[7] or "—"
        phone = row[8] or "—"
        is_active = row[12] if len(row) > 12 else 1

        card = tk.Frame(parent, bg=self.colors["card"], padx=12, pady=12)

        title = tk.Frame(card, bg=self.colors["card"])
        title.pack(fill="x")
        tk.Label(title, text=name, bg=self.colors["card"], fg=self.colors["text"],
                 font=("Arial", 11, "bold")).pack(side="left")
        status_text = "Active" if is_active else "Inactive"
        status_color = self.colors["accent"] if is_active else self.colors["muted"]
        tk.Label(title, text=status_text, bg=self.colors["card"], fg=status_color,
             font=("Arial", 9, "bold")).pack(side="right")
        tk.Label(title, text=emp_number, bg=self.colors["card"], fg=self.colors["muted"],
             font=("Arial", 9)).pack(side="right", padx=(0, 8))

        tk.Label(card, text=designation, bg=self.colors["card"], fg=self.colors["muted"],
                 font=("Arial", 9)).pack(anchor="w", pady=(4, 0))

        info = tk.Frame(card, bg=self.colors["card"])
        info.pack(fill="x", pady=(8, 0))
        tk.Label(info, text=f"Team: {team}", bg=self.colors["card"], fg=self.colors["text"],
                 font=("Arial", 9)).pack(anchor="w")
        tk.Label(info, text=f"Manager: {manager}", bg=self.colors["card"], fg=self.colors["text"],
                 font=("Arial", 9)).pack(anchor="w")
        tk.Label(info, text=f"Joined: {joining_date}", bg=self.colors["card"], fg=self.colors["text"],
                 font=("Arial", 9)).pack(anchor="w")

        contact = tk.Frame(card, bg=self.colors["card"])
        contact.pack(fill="x", pady=(8, 0))
        tk.Label(contact, text=f"Email: {email}", bg=self.colors["card"], fg=self.colors["text"],
                 font=("Arial", 9)).pack(anchor="w")
        tk.Label(contact, text=f"Phone: {phone}", bg=self.colors["card"], fg=self.colors["text"],
                 font=("Arial", 9)).pack(anchor="w")

        actions = tk.Frame(card, bg=self.colors["card"])
        actions.pack(fill="x", pady=(10, 0))
        ttk.Button(actions, text="Print ID Card", style="Info.TButton",
               command=lambda r=row: self.print_employee_id_card(r)).pack(side="left")
        if is_active:
            ttk.Button(actions, text="Deactivate", style="Danger.TButton",
                       command=lambda e=emp_id: self.set_employee_active(e, False)).pack(side="left", padx=6)
        else:
            ttk.Button(actions, text="Activate", style="Success.TButton",
                       command=lambda e=emp_id: self.set_employee_active(e, True)).pack(side="left", padx=6)

        return card

    def set_employee_active(self, emp_id: int, active: bool):
        """Activate or deactivate an employee."""
        try:
            if not active:
                messagebox.showwarning("Caution", "This will deactivate the employee and limit access/visibility.")
                if not messagebox.askyesno("Confirm", "Deactivate this employee?"):
                    return
            if self.hr_service.update_employee(emp_id, is_active=1 if active else 0):
                self.activity_service.log(self.current_user, "HR Status", f"Employee {emp_id} set to {'active' if active else 'inactive'}")
                self.refresh_hr_cards()
            else:
                messagebox.showerror("HR", "Failed to update employee status")
        except Exception as e:
            messagebox.showerror("HR", f"Failed to update status: {e}")

    def refresh_reports(self):
        """Refresh reports data and charts."""
        period_key = self.reports_period_map.get(self.reports_period_var.get(), "30")
        start_date, end_date, days = self.analytics_service.get_date_range(period_key)

        trend = self.analytics_service.get_sales_trend(start_date, end_date)
        summary = self.analytics_service.get_sales_summary(start_date, end_date)

        self._reports_trend = trend
        self._reports_summary = summary

        total_sales = sum(row[1] for row in trend) if trend else 0.0
        avg_daily = total_sales / max(1, days)
        items_sold = sum(row[1] for row in summary) if summary else 0
        top_item_name = summary[0][0] if summary else "—"

        self.reports_kpi["total_sales"].config(text=CurrencyFormatter.format_currency(total_sales))
        self.reports_kpi["avg_daily"].config(text=CurrencyFormatter.format_currency(avg_daily))
        self.reports_kpi["items_sold"].config(text=str(items_sold))
        self.reports_kpi["top_item"].config(text=top_item_name)

        self._draw_sales_trend(self.reports_sales_ax, trend)
        self.reports_sales_fig.patch.set_facecolor(self.colors["card"])
        self.reports_sales_canvas.draw()

        self._draw_top_items(self.reports_items_ax, summary)
        self.reports_items_fig.patch.set_facecolor(self.colors["card"])
        self.reports_items_canvas.draw()

    # === Bills helpers ===
    def _resize_bills_canvas(self, event):
        """Resize bills canvas to match container width."""
        self.bills_canvas.itemconfig(self.bills_canvas_window, width=event.width)

    def refresh_bills_timeline(self):
        """Refresh the bills timeline view."""
        if not hasattr(self, "bills_timeline_frame"):
            return
        for widget in self.bills_timeline_frame.winfo_children():
            widget.destroy()

        sales = self.pos_service.get_all_sales()
        if not sales:
            empty = tk.Frame(self.bills_timeline_frame, bg=self.colors["card"], padx=12, pady=12)
            empty.pack(fill="x", pady=6)
            tk.Label(empty, text="No sales history yet", bg=self.colors["card"], fg=self.colors["muted"]).pack(anchor="w")
            return

        # Group sales by date
        grouped = {}
        for row in sales:
            sale_date = str(row[1])
            sale_day = sale_date[:10]
            grouped.setdefault(sale_day, []).append(row)

        for day in sorted(grouped.keys(), reverse=True):
            day_card = tk.Frame(self.bills_timeline_frame, bg=self.colors["card"], padx=12, pady=10)
            day_card.pack(fill="x", pady=6)

            tk.Label(day_card, text=day, bg=self.colors["card"], fg=self.colors["text"],
                     font=("Arial", 10, "bold")).pack(anchor="w")

            for row in grouped[day]:
                _, sale_date, item_name, qty, sale_price, total_amount, username = row
                entry = tk.Frame(day_card, bg=self.colors["card"])
                entry.pack(fill="x", pady=4)

                left = tk.Frame(entry, bg=self.colors["card"])
                left.pack(side="left", fill="x", expand=True)
                tk.Label(left, text=item_name, bg=self.colors["card"], fg=self.colors["text"],
                         font=("Arial", 9, "bold")).pack(anchor="w")
                tk.Label(left, text=f"Qty: {qty} • By: {username}", bg=self.colors["card"],
                         fg=self.colors["muted"], font=("Arial", 9)).pack(anchor="w")

                right = tk.Frame(entry, bg=self.colors["card"])
                right.pack(side="right")
                tk.Label(right, text=CurrencyFormatter.format_currency(total_amount), bg=self.colors["card"],
                         fg=self.colors["text"], font=("Arial", 9, "bold")).pack(anchor="e")
                tk.Label(right, text=str(sale_date)[11:16], bg=self.colors["card"], fg=self.colors["muted"],
                         font=("Arial", 8)).pack(anchor="e")
                ttk.Button(right, text="Print", style="Info.TButton",
                           command=lambda r=row: self.print_sale_receipt(r)).pack(anchor="e", pady=(4, 0))

    # === Visitors helpers ===
    def _resize_vis_canvas(self, event):
        """Resize visitors canvas to match container width."""
        self.vis_canvas.itemconfig(self.vis_canvas_window, width=event.width)

    def reset_visitors_search(self):
        """Reset visitors search field and refresh cards."""
        self.vis_search_var.set("")
        self.refresh_visitors_cards()

    def refresh_visitors_cards(self):
        """Refresh visitor cards."""
        if not hasattr(self, "vis_cards_frame"):
            return
        for widget in self.vis_cards_frame.winfo_children():
            widget.destroy()

        query = (self.vis_search_var.get() or "").strip().lower()
        visitors = self.visitor_service.get_all_visitors()

        filtered = []
        for row in visitors:
            name = row[1] or ""
            phone = row[3] or ""
            email = row[4] or ""
            company = row[5] or ""
            if not query or any(query in str(v).lower() for v in [name, phone, email, company]):
                filtered.append(row)

        if not filtered:
            empty = tk.Frame(self.vis_cards_frame, bg=self.colors["card"], padx=12, pady=12)
            empty.pack(fill="x", pady=6)
            tk.Label(empty, text="No visitors found", bg=self.colors["card"], fg=self.colors["muted"]).pack(anchor="w")
            return

        for idx, row in enumerate(filtered):
            card = self._create_visitor_card(self.vis_cards_frame, row)
            r = idx // 2
            c = idx % 2
            card.grid(row=r, column=c, padx=6, pady=6, sticky="nsew")

        self.vis_cards_frame.grid_columnconfigure(0, weight=1)
        self.vis_cards_frame.grid_columnconfigure(1, weight=1)

    def _create_visitor_card(self, parent, row):
        """Build a single visitor card."""
        name = row[1] or "—"
        address = row[2] or "—"
        phone = row[3] or "—"
        email = row[4] or "—"
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
        tk.Label(contact, text=f"Email: {email}", bg=self.colors["card"], fg=self.colors["text"],
                 font=("Arial", 9)).pack(anchor="w")
        tk.Label(contact, text=f"Phone: {phone}", bg=self.colors["card"], fg=self.colors["text"],
                 font=("Arial", 9)).pack(anchor="w")

        return card

    # === Settings helpers ===
    def set_company_fields_state(self, state: str):
        """Enable/disable company info fields."""
        for entry in [
            self.company_name_entry,
            self.company_address_entry,
            self.company_phone_entry,
            self.company_email_entry,
            self.company_tax_entry,
            self.company_bank_entry,
        ]:
            entry.configure(state=state)

    def load_company_info(self):
        """Load company info and lock fields if already set."""
        info = self.company_service.get_info()
        if info:
            self.company_name_entry.delete(0, tk.END)
            self.company_name_entry.insert(0, info.get("company_name", ""))
            self.company_address_entry.delete(0, tk.END)
            self.company_address_entry.insert(0, info.get("address", ""))
            self.company_phone_entry.delete(0, tk.END)
            self.company_phone_entry.insert(0, info.get("phone", ""))
            self.company_email_entry.delete(0, tk.END)
            self.company_email_entry.insert(0, info.get("email", ""))
            self.company_tax_entry.delete(0, tk.END)
            self.company_tax_entry.insert(0, info.get("tax_id", ""))
            self.company_bank_entry.delete(0, tk.END)
            self.company_bank_entry.insert(0, info.get("bank_details", ""))

            self.set_company_fields_state("disabled")
            self.company_lock_status.config(text="Locked")
        else:
            self.set_company_fields_state("normal")
            self.company_lock_status.config(text="Unlocked")

    def save_company_info(self):
        """Save company info and lock fields."""
        name = self.company_name_entry.get().strip()
        address = self.company_address_entry.get().strip()
        phone = self.company_phone_entry.get().strip()
        email = self.company_email_entry.get().strip()
        tax_id = self.company_tax_entry.get().strip()
        bank_details = self.company_bank_entry.get().strip()

        if not name:
            messagebox.showerror("Company Info", "Company name is required")
            return

        self.company_service.save_info(name, address, phone, email, tax_id, bank_details)
        self.activity_service.log(self.current_user, "Company Info", "Company info updated")
        self.set_company_fields_state("disabled")
        self.company_lock_status.config(text="Locked")
        messagebox.showinfo("Company Info", "Company info saved and locked")

    def unlock_company_info(self):
        """Unlock company info for editing."""
        if messagebox.askyesno("Unlock", "Allow editing of Company Info?"):
            self.set_company_fields_state("normal")
            self.company_lock_status.config(text="Unlocked")

    def load_email_config(self):
        """Load email configuration into UI."""
        cfg = self.email_service.get_config()
        if not cfg:
            return
        self.smtp_server_entry.delete(0, tk.END)
        self.smtp_server_entry.insert(0, cfg.get("smtp_server", ""))
        self.smtp_port_entry.delete(0, tk.END)
        self.smtp_port_entry.insert(0, str(cfg.get("smtp_port", "")))
        self.sender_email_entry.delete(0, tk.END)
        self.sender_email_entry.insert(0, cfg.get("sender_email", ""))
        self.sender_password_entry.delete(0, tk.END)
        self.sender_password_entry.insert(0, cfg.get("sender_password", ""))
        self.recipient_email_entry.delete(0, tk.END)
        self.recipient_email_entry.insert(0, cfg.get("recipient_email", ""))

    def save_email_config(self):
        """Save email configuration."""
        smtp_server = self.smtp_server_entry.get().strip()
        smtp_port = self.smtp_port_entry.get().strip()
        sender_email = self.sender_email_entry.get().strip()
        sender_password = self.sender_password_entry.get().strip()
        recipient_email = self.recipient_email_entry.get().strip()

        if not smtp_server or not smtp_port or not sender_email or not sender_password or not recipient_email:
            messagebox.showerror("Email Settings", "All fields are required")
            return

        try:
            smtp_port = int(smtp_port)
        except ValueError:
            messagebox.showerror("Email Settings", "SMTP port must be a number")
            return

        self.email_service.save_config(smtp_server, smtp_port, sender_email, sender_password, recipient_email)
        self.activity_service.log(self.current_user, "Email Config", "Email settings updated")
        messagebox.showinfo("Email Settings", "Email settings saved")

    def test_email_config(self):
        """Send a test email."""
        try:
            self.email_service.send_email("BizHub Test", "This is a test email from BizHub.")
            messagebox.showinfo("Email Settings", "Test email sent")
        except Exception as e:
            messagebox.showerror("Email Settings", f"Test email failed: {e}")
    
    def show_visitors_for_quick_action(self):
        """Quick action for visitors."""
        count = self.visitor_service.get_total_visitors_count()
        messagebox.showinfo("Visitors", f"Total visitors: {count}")


if __name__ == "__main__":
    root = tk.Tk()
    app = BizHubDesktopApp(root)
    root.mainloop()
