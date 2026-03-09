"""Base class for all BizHub tab modules."""
import os
import subprocess
import tempfile
import tkinter as tk
from tkinter import ttk, messagebox


class BaseTab:
    """
    Base class for all BizHub tab modules.

    Each subclass:
    - Receives the parent notebook and the main BizHubDesktopApp instance
    - Creates its own frame, adds it to the notebook in _build()
    - Owns all its UI widgets as instance variables
    - Exposes a refresh() method for on-demand data reload

    Access pattern inside any tab:
        self.colors                 → current theme dict (auto-updates with dark mode)
        self.root                   → Tk root window (for Toplevel dialogs)
        self.app.<service>          → any service (inventory_service, pos_service, …)
        self.app.current_user       → logged-in username
        self.app.current_role       → user role string
    """

    def __init__(self, notebook: ttk.Notebook, app):
        self.notebook = notebook
        self.app = app
        self.frame = ttk.Frame(notebook)

    # ------------------------------------------------------------------
    # Convenience properties
    # ------------------------------------------------------------------

    @property
    def colors(self) -> dict:
        """Current theme color dict. Reflects dark/light mode automatically."""
        return self.app.colors

    @property
    def root(self) -> tk.Tk:
        """Tk root window reference."""
        return self.app.root

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def refresh(self):
        """Reload/refresh tab data. Override in subclasses as needed."""
        pass

    # ------------------------------------------------------------------
    # Shared print utilities (used by POS, HR, etc.)
    # ------------------------------------------------------------------

    def _show_print_preview(self, text: str, title: str):
        """Show a preview dialog for printable content."""
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

    def _print_text(self, text: str, job_name: str):
        """Send text to system printer (macOS/Linux via lp)."""
        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as tmp:
                tmp.write(text)
                tmp_path = tmp.name
            subprocess.run(["lp", "-t", job_name, tmp_path], check=True)
            self.app.activity_service.log(
                self.app.current_user or "system", "Print", job_name
            )
            messagebox.showinfo("Print", "Sent to printer.")
        except Exception as e:
            messagebox.showerror("Print Error", f"Failed to print: {e}")

    # ------------------------------------------------------------------
    # Shared UI helpers
    # ------------------------------------------------------------------

    def _make_field_row(self, parent, label_text: str, bg: str = None, width: int = 14):
        """Create a label+entry row. Returns the Entry widget."""
        bg = bg or self.colors["card"]
        row = tk.Frame(parent, bg=bg)
        row.pack(fill="x", pady=4)
        tk.Label(row, text=label_text, bg=bg, fg=self.colors["muted"],
                 width=width, anchor="w").pack(side="left")
        entry = ttk.Entry(row)
        entry.pack(side="left", fill="x", expand=True)
        return entry

    def _make_scrollable_canvas(self, parent):
        """Create a canvas+scrollbar pair. Returns (canvas, scroll, inner_frame, window_id)."""
        canvas = tk.Canvas(parent, bg=self.colors["bg"], highlightthickness=0)
        scroll = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scroll.set)

        scroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        inner = tk.Frame(canvas, bg=self.colors["bg"])
        window_id = canvas.create_window((0, 0), window=inner, anchor="nw")

        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfig(window_id, width=e.width))

        return canvas, scroll, inner, window_id
