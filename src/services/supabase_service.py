"""
SupabaseService: Handles Supabase database connection, authentication, and CRUD operations for BizHub.
"""
from supabase import create_client, Client

class SupabaseService:
    # === USERS & AUTH ===
    def fetch_users(self):
        return self.fetch_all("users")

    def add_user(self, data: dict):
        return self.insert("users", data)

    def update_user(self, user_id: str, data: dict):
        return self.update("users", "id", user_id, data)

    def delete_user(self, user_id: str):
        return self.delete("users", "id", user_id)

    # === INVENTORY ===
    def fetch_inventory(self):
        return self.fetch_all("inventory")

    def add_inventory_item(self, data: dict):
        return self.insert("inventory", data)

    def update_inventory_item(self, item_id: str, data: dict):
        return self.update("inventory", "id", item_id, data)

    def delete_inventory_item(self, item_id: str):
        return self.delete("inventory", "id", item_id)

    # === SALES ===
    def fetch_sales(self):
        return self.fetch_all("sales")

    def add_sale(self, data: dict):
        return self.insert("sales", data)

    # === EMPLOYEES ===
    def fetch_employees(self):
        return self.fetch_all("employees")

    def add_employee(self, data: dict):
        return self.insert("employees", data)

    def update_employee(self, emp_id: str, data: dict):
        return self.update("employees", "id", emp_id, data)

    def delete_employee(self, emp_id: str):
        return self.delete("employees", "id", emp_id)

    # === APPRAISALS ===
    def fetch_appraisals(self):
        return self.fetch_all("appraisals")

    def add_appraisal(self, data: dict):
        return self.insert("appraisals", data)

    # === GOALS ===
    def fetch_goals(self):
        return self.fetch_all("goals")

    def add_goal(self, data: dict):
        return self.insert("goals", data)

    # === VISITORS ===
    def fetch_visitors(self):
        return self.fetch_all("visitors")

    def add_visitor(self, data: dict):
        return self.insert("visitors", data)

    def update_visitor(self, visitor_id: str, data: dict):
        return self.update("visitors", "id", visitor_id, data)

    def delete_visitor(self, visitor_id: str):
        return self.delete("visitors", "id", visitor_id)

    # === EMAIL CONFIG ===
    def fetch_email_config(self):
        return self.fetch_all("email_config")

    def save_email_config(self, data: dict):
        return self.insert("email_config", data)

    # === COMPANY INFO ===
    def fetch_company_info(self):
        return self.fetch_all("company_info")

    def save_company_info(self, data: dict):
        return self.insert("company_info", data)

    # === ACTIVITY LOG ===
    def fetch_activity_log(self):
        return self.fetch_all("activity_log")

    def log_activity(self, data: dict):
        return self.insert("activity_log", data)

    # === PAYROLL ===
    def fetch_payroll(self):
        return self.fetch_all("payroll")

    def add_payroll(self, data: dict):
        return self.insert("payroll", data)

    # === APPRAISAL CYCLES ===
    def fetch_appraisal_cycles(self):
        return self.fetch_all("appraisal_cycles")

    def add_appraisal_cycle(self, data: dict):
        return self.insert("appraisal_cycles", data)

    # === FEEDBACK REQUESTS ===
    def fetch_feedback_requests(self):
        return self.fetch_all("feedback_requests")

    def add_feedback_request(self, data: dict):
        return self.insert("feedback_requests", data)

    # === FEEDBACK ENTRIES ===
    def fetch_feedback_entries(self):
        return self.fetch_all("feedback_entries")

    def add_feedback_entry(self, data: dict):
        return self.insert("feedback_entries", data)

    def __init__(self, url: str, key: str):
        self.url = url
        self.key = key
        self.client: Client = create_client(url, key)

    def sign_in(self, email: str, password: str):
        # Use sign_in_with_password for supabase-py v2+
        return self.client.auth.sign_in_with_password({"email": email, "password": password})

    def sign_up(self, email: str, password: str):
        # Use sign_up with correct argument structure for supabase-py v2+
        return self.client.auth.sign_up({"email": email, "password": password})

    def get_table(self, table_name: str):
        return self.client.table(table_name)

    def fetch_all(self, table_name: str):
        return self.client.table(table_name).select('*').execute()

    def insert(self, table_name: str, data: dict):
        return self.client.table(table_name).insert(data).execute()

    def update(self, table_name: str, id_field: str, id_value, data: dict):
        return self.client.table(table_name).update(data).eq(id_field, id_value).execute()

    def delete(self, table_name: str, id_field: str, id_value):
        return self.client.table(table_name).delete().eq(id_field, id_value).execute()

    def get_user(self):
        return self.client.auth.user()

    def sign_out(self):
        return self.client.auth.sign_out()
