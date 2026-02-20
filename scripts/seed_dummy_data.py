import sqlite3
from datetime import datetime, timedelta

from src.core import PasswordManager

DB_FILE = "inventory.db"

DUMMY_USERS = [
    ("admin", PasswordManager.hash_password("admin123"), "admin"),
    ("manager", PasswordManager.hash_password("manager123"), "admin"),
    ("staff1", PasswordManager.hash_password("staff123"), "user"),
    ("staff2", PasswordManager.hash_password("staff123"), "user"),
    ("staff3", PasswordManager.hash_password("staff123"), "user"),
    ("ops1", PasswordManager.hash_password("ops123"), "user"),
    ("sales1", PasswordManager.hash_password("sales123"), "user"),
    ("sales2", PasswordManager.hash_password("sales123"), "user"),
    ("hr1", PasswordManager.hash_password("hr123"), "user"),
    ("analyst1", PasswordManager.hash_password("analyst123"), "user"),
]

DUMMY_ITEMS = [
    ("Wireless Mouse", 45, 10, 8.50, 15.99, "Ergonomic wireless mouse"),
    ("Mechanical Keyboard", 30, 8, 35.00, 79.99, "RGB mechanical keyboard"),
    ("USB-C Hub", 60, 15, 12.00, 24.99, "6-in-1 USB-C hub"),
    ("27\" Monitor", 20, 5, 120.00, 199.99, "27-inch IPS monitor"),
    ("Laptop Stand", 80, 20, 7.00, 19.99, "Aluminum laptop stand"),
    ("Webcam 1080p", 35, 10, 18.00, 39.99, "Full HD webcam"),
    ("Noise Cancelling Headphones", 25, 5, 55.00, 129.99, "Over-ear headphones"),
    ("Desk Lamp", 50, 10, 9.00, 22.99, "LED desk lamp"),
    ("External SSD 1TB", 18, 4, 70.00, 139.99, "Portable SSD"),
    ("Office Chair", 12, 3, 80.00, 179.99, "Ergonomic office chair"),
]

DUMMY_VISITORS = [
    ("Alice Johnson", "12 Park Ave", "555-0101", "alice@example.com", "Acme Co", "Interested in bulk order"),
    ("Bob Smith", "88 Lake Rd", "555-0102", "bob@example.com", "Beta LLC", "Follow-up required"),
    ("Carla Gomez", "7 Hill St", "555-0103", "carla@example.com", "Gamma Inc", "New lead"),
    ("David Lee", "21 Oak Ln", "555-0104", "david@example.com", "Delta Ltd", "Requested catalog"),
    ("Emma Davis", "3 Pine Ct", "555-0105", "emma@example.com", "Epsilon Co", "Meeting scheduled"),
    ("Frank Moore", "44 Cedar Dr", "555-0106", "frank@example.com", "Foxtrot", "Call back"),
    ("Grace Kim", "9 Birch Blvd", "555-0107", "grace@example.com", "Helix", "Demo needed"),
    ("Henry Wong", "15 Elm St", "555-0108", "henry@example.com", "Ion Labs", "Potential partner"),
    ("Ivy Brown", "27 Maple Ave", "555-0109", "ivy@example.com", "Jade Group", "Pricing info"),
    ("Jack Patel", "60 River Rd", "555-0110", "jack@example.com", "Kappa Co", "Interested in subscription"),
]

DUMMY_EMPLOYEES = [
    ("EMP001", "John Carter", "2023-01-15", "Manager", "CEO", "Sales", "john@bz.com", "9000000001", "9000000002", "", "Top performer"),
    ("EMP002", "Sara Miles", "2023-03-20", "Supervisor", "John Carter", "Sales", "sara@bz.com", "9000000003", "9000000004", "", "Team lead"),
    ("EMP003", "Leo Park", "2023-05-11", "Engineer", "CTO", "Tech", "leo@bz.com", "9000000005", "9000000006", "", "Backend"),
    ("EMP004", "Nina Shah", "2023-07-01", "Designer", "CTO", "Tech", "nina@bz.com", "9000000007", "9000000008", "", "UI/UX"),
    ("EMP005", "Omar Ali", "2023-09-12", "Analyst", "CFO", "Finance", "omar@bz.com", "9000000009", "9000000010", "", "Reports"),
    ("EMP006", "Priya Rao", "2023-10-05", "HR", "COO", "HR", "priya@bz.com", "9000000011", "9000000012", "", "Hiring"),
    ("EMP007", "Quinn Lee", "2023-11-18", "Support", "COO", "Support", "quinn@bz.com", "9000000013", "9000000014", "", "Customer care"),
    ("EMP008", "Rita Singh", "2024-01-02", "Sales Rep", "John Carter", "Sales", "rita@bz.com", "9000000015", "9000000016", "", "Field sales"),
    ("EMP009", "Sam Torres", "2024-02-10", "Engineer", "CTO", "Tech", "sam@bz.com", "9000000017", "9000000018", "", "Frontend"),
    ("EMP010", "Tina Fox", "2024-03-22", "Admin", "COO", "Admin", "tina@bz.com", "9000000019", "9000000020", "", "Operations"),
]

DUMMY_COMPANY_INFO = [
    ("BzHub Inc.", "123 Business Ave", "555-1000", "info@bz.com", "TAX-123", "Bank: Demo Bank"),
    ("BzHub West", "45 Sunset Blvd", "555-1001", "west@bz.com", "TAX-124", "Bank: West Bank"),
    ("BzHub East", "78 Sunrise Dr", "555-1002", "east@bz.com", "TAX-125", "Bank: East Bank"),
    ("BzHub North", "9 Polar Rd", "555-1003", "north@bz.com", "TAX-126", "Bank: North Bank"),
    ("BzHub South", "22 Coastal Ave", "555-1004", "south@bz.com", "TAX-127", "Bank: South Bank"),
    ("BzHub Central", "300 Center St", "555-1005", "central@bz.com", "TAX-128", "Bank: Central Bank"),
    ("BzHub Retail", "11 Market Ln", "555-1006", "retail@bz.com", "TAX-129", "Bank: Retail Bank"),
    ("BzHub Online", "66 Cloud Way", "555-1007", "online@bz.com", "TAX-130", "Bank: Online Bank"),
    ("BzHub Services", "250 Service Rd", "555-1008", "services@bz.com", "TAX-131", "Bank: Service Bank"),
    ("BzHub Labs", "5 Innovation Park", "555-1009", "labs@bz.com", "TAX-132", "Bank: Lab Bank"),
]

DUMMY_EMAIL_CONFIGS = [
    ("smtp.example.com", 587, "noreply@bz.com", "password1", "alerts@bz.com"),
    ("smtp.example.com", 587, "reports@bz.com", "password2", "finance@bz.com"),
    ("smtp.mail.com", 465, "support@bz.com", "password3", "support@bz.com"),
    ("smtp.mail.com", 465, "sales@bz.com", "password4", "sales@bz.com"),
    ("smtp.mail.com", 587, "ops@bz.com", "password5", "ops@bz.com"),
    ("smtp.host.com", 587, "hr@bz.com", "password6", "hr@bz.com"),
    ("smtp.host.com", 587, "alerts@bz.com", "password7", "alerts@bz.com"),
    ("smtp.host.com", 465, "no-reply@bz.com", "password8", "admin@bz.com"),
    ("smtp.cloud.com", 587, "billing@bz.com", "password9", "billing@bz.com"),
    ("smtp.cloud.com", 465, "updates@bz.com", "password10", "updates@bz.com"),
]

DUMMY_ACTIVITY_LOGS = [
    ("admin", "Seed", "Initialized demo data"),
    ("manager", "Inventory", "Reviewed stock levels"),
    ("sales1", "Sales", "Recorded POS transaction"),
    ("sales2", "Sales", "Processed refund"),
    ("ops1", "Ops", "Updated supplier details"),
    ("hr1", "HR", "Added new employee"),
    ("analyst1", "Reports", "Generated sales report"),
    ("staff1", "POS", "Opened cash drawer"),
    ("staff2", "Inventory", "Adjusted thresholds"),
    ("staff3", "System", "Logged in"),
]


def clear_tables(cursor):
    tables = [
        "sales",
        "activity_log",
        "appraisals",
        "goals",
        "employees",
        "visitors",
        "inventory",
        "email_config",
        "company_info",
        "users",
    ]
    for table in tables:
        try:
            cursor.execute(f"DELETE FROM {table}")
        except Exception:
            pass


def seed_users(conn):
    cursor = conn.cursor()
    for username, password_hash, role in DUMMY_USERS:
        try:
            cursor.execute(
                "INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (username, password_hash, role),
            )
        except Exception:
            pass


def seed_inventory(conn):
    cursor = conn.cursor()
    for item in DUMMY_ITEMS:
        try:
            cursor.execute(
                "INSERT OR IGNORE INTO inventory (item_name, quantity, threshold, cost_price, sale_price, description) VALUES (?, ?, ?, ?, ?, ?)",
                item,
            )
        except Exception:
            pass


def seed_visitors(conn):
    cursor = conn.cursor()
    for v in DUMMY_VISITORS:
        try:
            cursor.execute(
                "INSERT INTO visitors (name, address, phone, email, company, notes) VALUES (?, ?, ?, ?, ?, ?)",
                v,
            )
        except Exception:
            pass


def seed_employees(conn):
    cursor = conn.cursor()
    for e in DUMMY_EMPLOYEES:
        try:
            cursor.execute(
                "INSERT OR IGNORE INTO employees (emp_number, name, joining_date, designation, manager, team, email, phone, emergency_contact, photo_path, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                e,
            )
        except Exception:
            pass


def seed_appraisals_goals(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM employees ORDER BY id LIMIT 10")
    emp_ids = [row[0] for row in cursor.fetchall()]

    for i, emp_id in enumerate(emp_ids):
        try:
            cursor.execute(
                "INSERT INTO appraisals (employee_id, appraisal_date, rating, comments) VALUES (?, ?, ?, ?)",
                (emp_id, "2024-12-31", "Good", f"Performance review {i + 1}"),
            )
        except Exception:
            pass

        try:
            cursor.execute(
                "INSERT INTO goals (employee_id, goal, status, due_date, notes) VALUES (?, ?, ?, ?, ?)",
                (emp_id, f"Goal {i + 1}", "In Progress", "2025-06-30", "Priority goal"),
            )
        except Exception:
            pass


def seed_sales(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT item_name, sale_price FROM inventory ORDER BY item_name LIMIT 10")
    items = cursor.fetchall()
    if not items:
        return

    usernames = [u[0] for u in DUMMY_USERS]
    for i in range(10):
        item_name, sale_price = items[i % len(items)]
        qty = (i % 5) + 1
        total_amount = qty * sale_price
        sale_date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d %H:%M:%S")
        username = usernames[i % len(usernames)]
        try:
            cursor.execute(
                "INSERT INTO sales (sale_date, item_name, quantity, sale_price, total_amount, username) VALUES (?, ?, ?, ?, ?, ?)",
                (sale_date, item_name, qty, sale_price, total_amount, username),
            )
        except Exception:
            pass


def seed_company_info(conn):
    cursor = conn.cursor()
    for company in DUMMY_COMPANY_INFO:
        try:
            cursor.execute(
                "INSERT INTO company_info (company_name, address, phone, email, tax_id, bank_details) VALUES (?, ?, ?, ?, ?, ?)",
                company,
            )
        except Exception:
            pass


def seed_email_config(conn):
    cursor = conn.cursor()
    for cfg in DUMMY_EMAIL_CONFIGS:
        try:
            cursor.execute(
                "INSERT INTO email_config (smtp_server, smtp_port, sender_email, sender_password, recipient_email) VALUES (?, ?, ?, ?, ?)",
                cfg,
            )
        except Exception:
            pass


def seed_activity_log(conn):
    cursor = conn.cursor()
    for log in DUMMY_ACTIVITY_LOGS:
        try:
            cursor.execute(
                "INSERT INTO activity_log (username, action, details) VALUES (?, ?, ?)",
                log,
            )
        except Exception:
            pass


def seed_all():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    clear_tables(cursor)

    seed_users(conn)
    seed_inventory(conn)
    seed_visitors(conn)
    seed_employees(conn)
    seed_appraisals_goals(conn)
    seed_sales(conn)
    seed_company_info(conn)
    seed_email_config(conn)
    seed_activity_log(conn)

    conn.commit()
    conn.close()
    print(
        "Seeded 10 rows each for users, inventory, visitors, employees, appraisals, goals, sales, company info, email config, activity log."
    )


if __name__ == "__main__":
    seed_all()
