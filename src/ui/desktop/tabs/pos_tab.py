"""Point-of-Sale (POS) tab — cart, checkout, and receipt printing."""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from src.core import CurrencyFormatter
from .base_tab import BaseTab


class POSTab(BaseTab):
    """POS with item search, quick-add, cart management, and receipt printing."""

    def __init__(self, notebook: ttk.Notebook, app, tab_label: str = "💳 POS"):
        super().__init__(notebook, app)
        self._tab_label = tab_label
        # Cart state
        self._cart: list[dict] = []
        self._selected_item: str | None = None
        self._qty_var = tk.StringVar(value="1")
        self._last_receipt_text: str = ""
        self._last_receipt_time: datetime | None = None
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
        ttk.Label(header, text="💳 POS", style="Header.TLabel").pack(side="left")
        ttk.Label(header, text="Quick add, search, and checkout",
                  style="Subheader.TLabel").pack(side="left", padx=10)

        body = tk.Frame(container, bg=self.colors["bg"])
        body.pack(fill="both", expand=True)

        # Left panel: item search + quick-add
        left = tk.Frame(body, bg=self.colors["card"], padx=12, pady=12)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        tk.Label(left, text="Inventory Search", bg=self.colors["card"],
                 fg=self.colors["text"], font=("Arial", 10, "bold")).pack(anchor="w")

        search_row = tk.Frame(left, bg=self.colors["card"])
        search_row.pack(fill="x", pady=(6, 6))
        self._search_entry = ttk.Entry(search_row)
        self._search_entry.pack(side="left", fill="x", expand=True)
        ttk.Button(search_row, text="Search", style="Info.TButton",
                   command=self._search_items).pack(side="left", padx=6)
        ttk.Button(search_row, text="Reset", style="Info.TButton",
                   command=self._load_items).pack(side="left")

        self._items_tree = ttk.Treeview(
            left, columns=("Item", "Qty", "Price"), show="headings", height=10
        )
        for col, text, width in [("Item", "Item", 200), ("Qty", "Qty", 60), ("Price", "Price", 80)]:
            self._items_tree.heading(col, text=text)
            self._items_tree.column(col, anchor="center", width=width)
        self._items_tree.pack(fill="both", expand=True, pady=(4, 8))
        self._items_tree.bind("<Double-1>", self._add_selected_to_cart)

        tk.Label(left, text="Quick Add", bg=self.colors["card"],
                 fg=self.colors["text"], font=("Arial", 10, "bold")).pack(anchor="w")
        self._quick_add_frame = tk.Frame(left, bg=self.colors["card"])
        self._quick_add_frame.pack(fill="x", pady=(6, 0))

        # Right panel: cart + controls
        right = tk.Frame(body, bg=self.colors["card"], padx=12, pady=12)
        right.pack(side="left", fill="both", expand=True)

        tk.Label(right, text="Cart", bg=self.colors["card"],
                 fg=self.colors["text"], font=("Arial", 10, "bold")).pack(anchor="w")

        self._cart_tree = ttk.Treeview(
            right, columns=("Item", "Qty", "Price", "Total"), show="headings", height=10
        )
        for col, text, width in [
            ("Item", "Item", 200), ("Qty", "Qty", 60),
            ("Price", "Price", 80), ("Total", "Total", 90),
        ]:
            self._cart_tree.heading(col, text=text)
            self._cart_tree.column(col, anchor="center", width=width)
        self._cart_tree.pack(fill="both", expand=True, pady=(4, 8))
        self._cart_tree.bind("<Double-1>", self._select_cart_item)

        totals_row = tk.Frame(right, bg=self.colors["card"])
        totals_row.pack(fill="x", pady=(0, 10))
        tk.Label(totals_row, text="Total", bg=self.colors["card"],
                 fg=self.colors["muted"]).pack(side="left")
        self._total_label = tk.Label(
            totals_row, text=CurrencyFormatter.format_currency(0),
            bg=self.colors["card"], fg=self.colors["text"], font=("Arial", 14, "bold"),
        )
        self._total_label.pack(side="right")

        qty_row = tk.Frame(right, bg=self.colors["card"])
        qty_row.pack(fill="x", pady=(0, 8))
        tk.Label(qty_row, text="Qty", bg=self.colors["card"],
                 fg=self.colors["muted"]).pack(side="left")
        ttk.Entry(qty_row, textvariable=self._qty_var, width=8).pack(side="left", padx=8)
        ttk.Button(qty_row, text="Update Qty", style="Primary.TButton",
                   command=self._update_cart_qty).pack(side="left")
        ttk.Button(qty_row, text="Remove", style="Danger.TButton",
                   command=self._remove_cart_item).pack(side="left", padx=6)

        checkout_row = tk.Frame(right, bg=self.colors["card"])
        checkout_row.pack(fill="x")
        ttk.Button(checkout_row, text="Checkout",     style="Success.TButton",
                   command=self.checkout).pack(side="left")
        ttk.Button(checkout_row, text="Print Receipt", style="Info.TButton",
                   command=self.print_last_receipt).pack(side="left", padx=6)
        ttk.Button(checkout_row, text="Clear Cart",   style="Danger.TButton",
                   command=self._clear_cart).pack(side="left", padx=6)

        self._load_items()
        self._load_quick_add()

    # ------------------------------------------------------------------
    # Item list helpers
    # ------------------------------------------------------------------

    def _load_items(self):
        for row in self._items_tree.get_children():
            self._items_tree.delete(row)
        for item in self.app.inventory_service.get_all_items():
            self._items_tree.insert("", "end", values=(
                item[0], item[1], CurrencyFormatter.format_currency(item[4])
            ))

    def _search_items(self):
        query = self._search_entry.get().strip()
        items = (self.app.inventory_service.search(query) if query
                 else self.app.inventory_service.get_all_items())
        for row in self._items_tree.get_children():
            self._items_tree.delete(row)
        for item in items:
            self._items_tree.insert("", "end", values=(
                item[0], item[1], CurrencyFormatter.format_currency(item[4])
            ))

    def _load_quick_add(self):
        for w in self._quick_add_frame.winfo_children():
            w.destroy()
        start, end, _ = self.app.analytics_service.get_date_range("7")
        top = self.app.analytics_service.get_top_selling_items(start, end, limit=6)
        if not top:
            items = self.app.inventory_service.get_all_items()[:6]
            top = [(i[0], i[1], i[4]) for i in items]
        for idx, item in enumerate(top):
            name = item[0]
            ttk.Button(
                self._quick_add_frame, text=name, style="Primary.TButton",
                command=lambda n=name: self._add_by_name(n),
            ).grid(row=idx // 3, column=idx % 3, padx=4, pady=4, sticky="ew")

    # ------------------------------------------------------------------
    # Cart actions
    # ------------------------------------------------------------------

    def _add_by_name(self, name: str):
        self._selected_item = name
        self._add_selected_to_cart()

    def _add_selected_to_cart(self, event=None):
        if event is not None:
            sel = self._items_tree.selection()
            if sel:
                self._selected_item = self._items_tree.item(sel[0])["values"][0]

        if not self._selected_item:
            sel = self._items_tree.selection()
            if sel:
                self._selected_item = self._items_tree.item(sel[0])["values"][0]

        if not self._selected_item:
            messagebox.showerror("POS", "Select an item to add")
            return

        try:
            qty = int(self._qty_var.get())
            if qty <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("POS", "Quantity must be a positive number")
            return

        item = self.app.inventory_service.get_item(self._selected_item)
        if not item:
            messagebox.showerror("POS", "Item not found")
            return

        price = item.get("sale_price", 0)
        existing = next((i for i in self._cart if i["item_name"] == self._selected_item), None)
        if existing:
            existing["quantity"] += qty
        else:
            self._cart.append({"item_name": self._selected_item, "quantity": qty, "price": price})
        self._refresh_cart()

    def _select_cart_item(self, event=None):
        sel = self._cart_tree.selection()
        if sel:
            vals = self._cart_tree.item(sel[0])["values"]
            self._selected_item = vals[0]
            self._qty_var.set(str(vals[1]))

    def _update_cart_qty(self):
        if not self._selected_item:
            messagebox.showerror("POS", "Select a cart item")
            return
        try:
            qty = int(self._qty_var.get())
            if qty <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("POS", "Quantity must be a positive number")
            return
        for item in self._cart:
            if item["item_name"] == self._selected_item:
                item["quantity"] = qty
                break
        self._refresh_cart()

    def _remove_cart_item(self):
        if not self._selected_item:
            messagebox.showerror("POS", "Select a cart item")
            return
        messagebox.showwarning("Caution", "This will remove the selected item from the cart.")
        if not messagebox.askyesno("Confirm", "Remove the selected cart item?"):
            return
        self._cart = [i for i in self._cart if i["item_name"] != self._selected_item]
        self._selected_item = None
        self._refresh_cart()

    def _clear_cart(self):
        messagebox.showwarning("Caution", "This will clear all items from the cart.")
        if not messagebox.askyesno("Confirm", "Clear the entire cart?"):
            return
        self._cart = []
        self._selected_item = None
        self._refresh_cart()

    def _refresh_cart(self):
        for row in self._cart_tree.get_children():
            self._cart_tree.delete(row)
        total = 0.0
        for item in self._cart:
            line_total = item["quantity"] * item["price"]
            total += line_total
            self._cart_tree.insert("", "end", values=(
                item["item_name"], item["quantity"],
                CurrencyFormatter.format_currency(item["price"]),
                CurrencyFormatter.format_currency(line_total),
            ))
        self._total_label.config(text=CurrencyFormatter.format_currency(total))

    # ------------------------------------------------------------------
    # Checkout
    # ------------------------------------------------------------------

    def checkout(self):
        if not self._cart:
            messagebox.showerror("POS", "Cart is empty")
            return

        sale_time = datetime.now()
        receipt = self._build_receipt(self._cart, sale_time, self.app.current_user)
        self._last_receipt_text = receipt
        self._last_receipt_time = sale_time

        for item in self._cart:
            name  = item["item_name"]
            qty   = item["quantity"]
            price = item["price"]
            self.app.pos_service.record_sale(name, qty, price, self.app.current_user)
            current = self.app.inventory_service.get_item(name)
            if current:
                new_qty = max(0, (current.get("quantity", 0) - qty))
                self.app.inventory_service.update_item(name, quantity=new_qty)

        self.app.activity_service.log(
            self.app.current_user, "POS Checkout",
            f"Processed {len(self._cart)} items",
        )
        self._clear_cart.__wrapped__ = None  # skip confirmation for post-checkout clear
        self._cart = []
        self._selected_item = None
        self._refresh_cart()
        self._load_items()
        self._load_quick_add()
        messagebox.showinfo("POS", "Sale completed")

    # ------------------------------------------------------------------
    # Receipt helpers (also used by BillsTab)
    # ------------------------------------------------------------------

    def print_last_receipt(self):
        if not self._last_receipt_text:
            messagebox.showerror("POS", "No receipt to print. Checkout first.")
            return
        self._show_print_preview(self._last_receipt_text, "BzHub POS Receipt")

    def print_sale_receipt(self, sale_row):
        """Print a single sale row (from Bills timeline)."""
        text = self._build_single_sale_receipt(sale_row)
        self._show_print_preview(text, "BzHub Sale Receipt")

    def _build_receipt(self, items: list, sale_time: datetime, username: str) -> str:
        info = self.app.company_service.get_info() or {}
        company_name = info.get("company_name") or "BzHub"
        address = info.get("address") or ""
        phone   = info.get("phone") or ""
        email   = info.get("email") or ""

        lines = [company_name]
        if address:
            lines.append(address)
        contact = " · ".join(v for v in [phone, email] if v)
        if contact:
            lines.append(contact)
        lines += [
            "=" * 48,
            f"Date: {sale_time.strftime('%Y-%m-%d %H:%M')}",
        ]
        if username:
            lines.append(f"User: {username}")
        lines += [
            "-" * 48,
            f"{'Item':<24}{'Qty':>4}{'Price':>10}{'Total':>10}",
            "-" * 48,
        ]
        subtotal = 0.0
        for item in items:
            name  = item["item_name"][:24]
            qty   = item["quantity"]
            price = item["price"]
            total = qty * price
            subtotal += total
            lines.append(f"{name:<24}{qty:>4}{price:>10.2f}{total:>10.2f}")

        lines += [
            "-" * 48,
            f"{'TOTAL':>38}{subtotal:>10.2f}",
            "=" * 48,
            "Thank you for your business!",
        ]
        return "\n".join(lines)

    def _build_single_sale_receipt(self, row) -> str:
        _, sale_date, item_name, qty, sale_price, total_amount, username = row
        lines = [
            "BzHub Sale Receipt",
            "=" * 48,
            f"Date: {sale_date}",
        ]
        if username:
            lines.append(f"User: {username}")
        lines += [
            "-" * 48,
            f"Item:  {item_name}",
            f"Qty:   {qty}",
            f"Price: {sale_price:.2f}",
            f"Total: {total_amount:.2f}",
            "=" * 48,
        ]
        return "\n".join(lines)
