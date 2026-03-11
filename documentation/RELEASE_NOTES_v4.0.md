# BzHub v4.0.0 — Release Notes
**Date:** 2026-03-11
**Status:** Stable

---

## What's New in v4.0

### Web Frontend (Next.js)

#### Dashboard
- **Fast & Slow Movers** — New section showing top 5 fast-moving and bottom 5 slow-moving products by units sold (last 30 days)
- **Compact inventory value** — Large rupee values now display in K / L / Cr format to prevent card overflow
- **Low Stock clickable** — "Needs attention" badge on the Low Stock KPI card navigates directly to `/operations?filter=lowstock`
- **Dynamic currency symbol** — All `$` symbols replaced with the currency selected in Settings (defaults to ₹)

#### Operations — Inventory
- **Image upload** — Add/edit items with a product image; stored as base64, shown as thumbnail in table and POS cards
- **Cost Price column** — Visible alongside Sale Price in the inventory table
- **Sortable columns** — Click Name, Qty, Cost, Price, or Status to sort ascending/descending
- **Stock status gradient** — Status badges use 5 levels of red (In Stock → Low Stock → Very Low → Critical → Out of Stock)
- **Low Stock filter** — Direct link from Dashboard routes to pre-filtered low stock view

#### Operations — POS
- **Product image thumbnails** — Each product card shows its image (or a placeholder icon)
- **Fixed ₹NaN** — Sale price now correctly parsed from API response

#### Operations — Bills
- **Isolated print** — Clicking Print opens a new popup window with only the receipt; auto-prints and closes (no more full-page print)
- **Sortable columns** — Sort by Date, Item, Qty, or Total

### Backend (FastAPI)
- **`/dashboard/product-velocity`** — New endpoint returning fast/slow movers based on sales data
- **`_row_to_dict` fix** — Corrected column index mapping for inventory rows (was causing NaN/TypeError across POS and inventory)
- **Dashboard KPI fix** — Inventory value now correctly calculated as `qty × cost_price`; low stock count uses `qty ≤ threshold`
- **Image path support** — `image_path` field added to inventory Pydantic models and persisted to SQLite

### DevOps
- **`start.sh` fixed** — Now uses `.venv/bin/python` directly, eliminating wrong-interpreter startup failures
- **Prompts log** — All user requests now logged to `memory/prompts_log.md` across sessions

---

## Bug Fixes
| Bug | Fix |
|-----|-----|
| `TypeError: i.item_name.toLowerCase is not a function` | Fixed `_row_to_dict` column index mapping |
| POS showing `₹NaN` | Same root cause — `sale_price` was receiving description string |
| Inventory Value overflowing KPI card | `compactINR()` formatter applied |
| Print bill printing entire page | Replaced with `window.open()` isolated receipt |
| API startup using wrong Python | `start.sh` now calls `.venv/bin/python` explicitly |
| `/dashboard/product-velocity` returning 404 | Old process was running stale code; fixed startup script |

---

## Previous Releases
- v3.1.0 — CRM Kanban, lead scoring, follow-ups
- v3.0 — Odoo-inspired CRM features
- v2.0 — Web frontend (Next.js + shadcn/ui) introduced
- v1.0.0 — Initial desktop app release
