"""Seed home-appliance inventory data via the BzHub API.

Usage (with API running on port 8000):
    source .venv/bin/activate
    python scripts/seed_inventory.py
"""
import sys
import requests

BASE = "http://localhost:8000/inventory"

ITEMS = [
    # name, qty, threshold, cost, sale, description
    # --- In Stock ---
    ("Samsung 55\" OLED TV",      12,  5, 42000, 49999, "Electronics"),
    ("Philips Air Fryer 4.5L",    15, 10,  4500,  6499, "Kitchen"),
    ("Voltas 1.5 Ton Split AC",    6,  4, 32000, 38999, "Cooling"),
    ("Crompton Ceiling Fan 48\"", 20, 15,  1200,  1799, "Cooling"),
    ("Bajaj Mixer Grinder 750W",   8, 10,  2200,  2999, "Kitchen"),
    # --- Low Stock (ratio 0.51–1.0 → light red) ---
    ("Sony Soundbar HT-A7000",     4,  6, 28000, 34999, "Electronics"),
    ("LG Front Load Washer 8kg",   5,  8, 35000, 42999, "Laundry"),
    # --- Very Low (ratio 0.26–0.50 → medium red) ---
    ("LG Refrigerator 350L",       3,  8, 26000, 31999, "Kitchen"),
    ("Dyson V15 Vacuum Cleaner",   2,  4, 38000, 44999, "Cleaning"),
    # --- Critical (ratio ≤ 0.25 → bright red) ---
    ("Whirlpool Washing Machine",  1,  5, 22000, 27999, "Laundry"),
    ("Havells Geyser 15L",         1,  8,  6500,  8999, "Bathroom"),
    # --- Out of Stock (darkest red) ---
    ("Bosch Built-in Dishwasher",  0,  3, 45000, 54999, "Kitchen"),
    ("Panasonic Microwave Oven",   0,  5,  8000, 10999, "Kitchen"),
]


def seed():
    added, skipped = 0, 0
    for name, qty, threshold, cost, sale, desc in ITEMS:
        payload = {
            "item_name": name,
            "quantity": qty,
            "threshold": threshold,
            "cost_price": cost,
            "sale_price": sale,
            "description": desc,
        }
        r = requests.post(BASE, json=payload, timeout=5)
        if r.status_code == 201:
            print(f"  + {name}")
            added += 1
        elif r.status_code == 409:
            print(f"  ~ {name} (already exists, skipped)")
            skipped += 1
        else:
            print(f"  ! {name} — {r.status_code}: {r.text}", file=sys.stderr)
    print(f"\nDone: {added} added, {skipped} skipped.")


if __name__ == "__main__":
    try:
        seed()
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to API at http://localhost:8000")
        print("Make sure the API is running:  python bizhub.py --api")
        sys.exit(1)
