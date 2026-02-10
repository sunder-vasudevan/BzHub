"""SQLite implementation of DatabaseAdapter - for local/desktop use."""
import sqlite3
from datetime import datetime
from src.db.base import DatabaseAdapter
from src.core import PasswordManager


class SQLiteAdapter(DatabaseAdapter):
    """SQLite database adapter - implements abstract DatabaseAdapter interface."""
    
    def __init__(self, db_file: str = "inventory.db"):
        self.db_file = db_file
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with all tables."""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        # Inventory table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT UNIQUE NOT NULL,
                quantity INTEGER DEFAULT 0,
                threshold INTEGER DEFAULT 0,
                cost_price REAL DEFAULT 0,
                sale_price REAL DEFAULT 0,
                description TEXT,
                image_path TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Sales table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                item_name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                sale_price REAL NOT NULL,
                total_amount REAL NOT NULL,
                username TEXT NOT NULL,
                FOREIGN KEY(username) REFERENCES users(username)
            )
        ''')
        
        # Email config table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                smtp_server TEXT,
                smtp_port INTEGER,
                sender_email TEXT,
                sender_password TEXT,
                recipient_email TEXT
            )
        ''')
        
        # Company info table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS company_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT,
                address TEXT,
                phone TEXT,
                email TEXT,
                tax_id TEXT,
                bank_details TEXT
            )
        ''')
        
        # Activity log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                username TEXT NOT NULL,
                action TEXT NOT NULL,
                details TEXT,
                FOREIGN KEY(username) REFERENCES users(username)
            )
        ''')
        
        # Visitors table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS visitors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                address TEXT,
                phone TEXT,
                email TEXT,
                company TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Employees table (HR)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                emp_number TEXT UNIQUE,
                name TEXT NOT NULL,
                joining_date TEXT,
                designation TEXT,
                manager TEXT,
                team TEXT,
                email TEXT,
                phone TEXT,
                emergency_contact TEXT,
                photo_path TEXT,
                notes TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Appraisals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS appraisals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL,
                appraisal_date TEXT,
                rating TEXT,
                comments TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(employee_id) REFERENCES employees(id)
            )
        ''')

        # Goals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL,
                goal TEXT NOT NULL,
                status TEXT,
                due_date TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(employee_id) REFERENCES employees(id)
            )
        ''')

        # Payroll table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payrolls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL,
                period_start TEXT,
                period_end TEXT,
                base_salary REAL DEFAULT 0,
                allowances REAL DEFAULT 0,
                deductions REAL DEFAULT 0,
                overtime_hours REAL DEFAULT 0,
                overtime_rate REAL DEFAULT 0,
                gross_pay REAL DEFAULT 0,
                net_pay REAL DEFAULT 0,
                status TEXT DEFAULT 'Draft',
                paid_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(employee_id) REFERENCES employees(id)
            )
        ''')

        # Appraisal cycles
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS appraisal_cycles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL,
                period_start TEXT,
                period_end TEXT,
                status TEXT DEFAULT 'Draft',
                self_text TEXT,
                self_rating REAL,
                manager_text TEXT,
                manager_rating REAL,
                final_rating REAL,
                created_by TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(employee_id) REFERENCES employees(id)
            )
        ''')

        # Feedback requests
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                appraisal_id INTEGER,
                requester TEXT,
                target_employee_id INTEGER NOT NULL,
                message TEXT,
                status TEXT DEFAULT 'Requested',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(appraisal_id) REFERENCES appraisal_cycles(id),
                FOREIGN KEY(target_employee_id) REFERENCES employees(id)
            )
        ''')

        # Feedback entries
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                appraisal_id INTEGER,
                from_employee_id INTEGER,
                to_employee_id INTEGER NOT NULL,
                rating REAL,
                feedback_text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(appraisal_id) REFERENCES appraisal_cycles(id),
                FOREIGN KEY(from_employee_id) REFERENCES employees(id),
                FOREIGN KEY(to_employee_id) REFERENCES employees(id)
            )
        ''')
        
        # Migrate employees table if new columns need to be added
        try:
            cursor.execute('PRAGMA table_info(employees)')
            existing_cols = {row[1] for row in cursor.fetchall()}
            required_cols = {'emp_number', 'emergency_contact', 'photo_path', 'is_active'}
            for col in required_cols:
                if col not in existing_cols:
                    if col == 'is_active':
                        cursor.execute('ALTER TABLE employees ADD COLUMN is_active INTEGER DEFAULT 1')
                    else:
                        cursor.execute(f'ALTER TABLE employees ADD COLUMN {col} TEXT')
        except Exception:
            pass

        # Migrate inventory table if new columns need to be added
        try:
            cursor.execute('PRAGMA table_info(inventory)')
            existing_cols = {row[1] for row in cursor.fetchall()}
            if 'image_path' not in existing_cols:
                cursor.execute('ALTER TABLE inventory ADD COLUMN image_path TEXT')
        except Exception:
            pass
        
        # Create default admin user if not exists
        self.create_admin_user('admin', PasswordManager.hash_password('admin123'))
        
        conn.commit()
        conn.close()
    
    # === USERS & AUTH ===
    
    def create_admin_user(self, username: str, password_hash: str):
        """Create default admin user if not exists."""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            if not cursor.fetchone():
                cursor.execute(
                    'INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)',
                    (username, password_hash, 'admin')
                )
                conn.commit()
        except Exception as e:
            print(f"Error creating admin user: {e}")
        finally:
            conn.close()
    
    def authenticate_user(self, username: str, password_hash: str) -> bool:
        """Verify user credentials."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM users WHERE username = ? AND password_hash = ?',
                (username, password_hash)
            )
            result = cursor.fetchone()
            conn.close()
            return result is not None
        except Exception:
            return False
    
    def get_user_role(self, username: str) -> str:
        """Get user role (admin, user, etc)."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute('SELECT role FROM users WHERE username = ?', (username,))
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else 'user'
        except Exception:
            return 'user'
    
    def update_last_login(self, username: str):
        """Update user's last login timestamp."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE username = ?',
                (username,)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error updating last login: {e}")
    
    # === INVENTORY ===
    
    def get_all_inventory(self) -> list:
        """Get all inventory items."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute('SELECT item_name, quantity, threshold, cost_price, sale_price, description FROM inventory ORDER BY item_name')
            rows = cursor.fetchall()
            conn.close()
            return rows
        except Exception:
            return []
    
    def get_inventory_by_name(self, name: str) -> dict:
        """Get inventory item by name."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM inventory WHERE item_name = ?', (name,))
            row = cursor.fetchone()
            conn.close()
            if row:
                return {
                    'id': row[0], 'item_name': row[1], 'quantity': row[2],
                    'threshold': row[3], 'cost_price': row[4], 'sale_price': row[5],
                    'description': row[6], 'image_path': row[7]
                }
            return None
        except Exception:
            return None
    
    def add_inventory_item(self, item_name: str, quantity: int, threshold: int,
                          cost_price: float, sale_price: float, description: str,
                          image_path: str = None):
        """Add new inventory item."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO inventory (item_name, quantity, threshold, cost_price, sale_price, description, image_path) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (item_name, quantity, threshold, cost_price, sale_price, description, image_path)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding inventory item: {e}")
            return False
    
    def update_inventory_item(self, item_name: str, quantity: int = None,
                             threshold: int = None, cost_price: float = None,
                             sale_price: float = None, description: str = None,
                             image_path: str = None):
        """Update inventory item."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            updates = []
            values = []
            if quantity is not None:
                updates.append('quantity = ?')
                values.append(quantity)
            if threshold is not None:
                updates.append('threshold = ?')
                values.append(threshold)
            if cost_price is not None:
                updates.append('cost_price = ?')
                values.append(cost_price)
            if sale_price is not None:
                updates.append('sale_price = ?')
                values.append(sale_price)
            if description is not None:
                updates.append('description = ?')
                values.append(description)
            if image_path is not None:
                updates.append('image_path = ?')
                values.append(image_path)
            
            if updates:
                updates.append('updated_at = CURRENT_TIMESTAMP')
                values.append(item_name)
                query = f'UPDATE inventory SET {", ".join(updates)} WHERE item_name = ?'
                cursor.execute(query, values)
                conn.commit()
            
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating inventory item: {e}")
            return False
    
    def delete_inventory_item(self, item_name: str):
        """Delete inventory item."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM inventory WHERE item_name = ?', (item_name,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting inventory item: {e}")
            return False
    
    def search_inventory(self, query: str) -> list:
        """Search inventory by name or description."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            q = f"%{query}%"
            cursor.execute('SELECT item_name, quantity, threshold, cost_price, sale_price, description FROM inventory WHERE item_name LIKE ? OR description LIKE ? ORDER BY item_name', (q, q))
            rows = cursor.fetchall()
            conn.close()
            return rows
        except Exception:
            return []
    
    # === SALES & POS ===
    
    def record_sale(self, item_name: str, quantity: int, sale_price: float,
                   total_amount: float, username: str):
        """Record a sale transaction."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO sales (item_name, quantity, sale_price, total_amount, username) VALUES (?, ?, ?, ?, ?)',
                (item_name, quantity, sale_price, total_amount, username)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error recording sale: {e}")
            return False
    
    def get_sales_by_date(self, date_str: str) -> list:
        """Get all sales for a specific date."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM sales WHERE DATE(sale_date) = ?', (date_str,))
            rows = cursor.fetchall()
            conn.close()
            return rows
        except Exception:
            return []
    
    def get_all_sales(self) -> list:
        """Get all sales transactions."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM sales ORDER BY sale_date DESC')
            rows = cursor.fetchall()
            conn.close()
            return rows
        except Exception:
            return []

    def get_sales_between(self, start_date: str, end_date: str) -> list:
        """Get all sales between start_date and end_date (inclusive)."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM sales WHERE DATE(sale_date) BETWEEN ? AND ? ORDER BY sale_date ASC',
                (start_date, end_date)
            )
            rows = cursor.fetchall()
            conn.close()
            return rows
        except Exception:
            return []

    def get_sales_summary_by_item(self, start_date: str, end_date: str) -> list:
        """Get sales summary grouped by item between dates."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute(
                '''
                SELECT item_name, SUM(quantity) as total_qty, SUM(total_amount) as total_amount
                FROM sales
                WHERE DATE(sale_date) BETWEEN ? AND ?
                GROUP BY item_name
                ORDER BY total_qty DESC
                ''',
                (start_date, end_date)
            )
            rows = cursor.fetchall()
            conn.close()
            return rows
        except Exception:
            return []

    def get_sales_trend_by_day(self, start_date: str, end_date: str) -> list:
        """Get sales totals grouped by day between dates."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute(
                '''
                SELECT DATE(sale_date) as sale_day, SUM(total_amount) as total_amount
                FROM sales
                WHERE DATE(sale_date) BETWEEN ? AND ?
                GROUP BY DATE(sale_date)
                ORDER BY sale_day ASC
                ''',
                (start_date, end_date)
            )
            rows = cursor.fetchall()
            conn.close()
            return rows
        except Exception:
            return []
    
    # === HR ===
    
    def add_employee(self, emp_number: str, name: str, joining_date: str,
                    designation: str, manager: str, team: str, email: str,
                    phone: str, emergency_contact: str, photo_path: str, notes: str,
                    is_active: int = 1):
        """Add new employee."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO employees (emp_number, name, joining_date, designation, manager, team, email, phone, emergency_contact, photo_path, notes, is_active) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (emp_number, name, joining_date, designation, manager, team, email, phone, emergency_contact, photo_path, notes, is_active)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding employee: {e}")
            return False
    
    def get_all_employees(self) -> list:
        """Get all employees."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute(
                'SELECT id, emp_number, name, joining_date, designation, manager, team, email, phone, emergency_contact, photo_path, notes, is_active FROM employees ORDER BY name'
            )
            rows = cursor.fetchall()
            conn.close()
            return rows
        except Exception:
            return []
    
    def get_employee_by_id(self, emp_id: int) -> dict:
        """Get employee by ID."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute(
                'SELECT id, emp_number, name, joining_date, designation, manager, team, email, phone, emergency_contact, photo_path, notes, is_active FROM employees WHERE id = ?',
                (emp_id,)
            )
            row = cursor.fetchone()
            conn.close()
            if row:
                return {
                    'id': row[0], 'emp_number': row[1], 'name': row[2],
                    'joining_date': row[3], 'designation': row[4], 'manager': row[5],
                    'team': row[6], 'email': row[7], 'phone': row[8],
                    'emergency_contact': row[9], 'photo_path': row[10], 'notes': row[11],
                    'is_active': row[12]
                }
            return None
        except Exception:
            return None
    
    def update_employee(self, emp_id: int, **kwargs):
        """Update employee details."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            allowed_fields = {'name', 'joining_date', 'designation', 'manager', 'team', 'email', 'phone', 'emergency_contact', 'photo_path', 'notes', 'is_active'}
            updates = []
            values = []
            
            for key, value in kwargs.items():
                if key in allowed_fields and value is not None:
                    updates.append(f'{key} = ?')
                    values.append(value)
            
            if updates:
                updates.append('updated_at = CURRENT_TIMESTAMP')
                values.append(emp_id)
                query = f'UPDATE employees SET {", ".join(updates)} WHERE id = ?'
                cursor.execute(query, values)
                conn.commit()
            
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating employee: {e}")
            return False
    
    def delete_employee(self, emp_id: int):
        """Delete employee."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM employees WHERE id = ?', (emp_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting employee: {e}")
            return False

    # === PAYROLL ===

    def add_payroll(self, employee_id: int, period_start: str, period_end: str,
                    base_salary: float, allowances: float, deductions: float,
                    overtime_hours: float, overtime_rate: float, gross_pay: float,
                    net_pay: float, status: str, paid_date: str):
        """Add payroll record."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute(
                '''
                INSERT INTO payrolls (employee_id, period_start, period_end, base_salary, allowances, deductions,
                                     overtime_hours, overtime_rate, gross_pay, net_pay, status, paid_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (employee_id, period_start, period_end, base_salary, allowances, deductions,
                 overtime_hours, overtime_rate, gross_pay, net_pay, status, paid_date)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding payroll: {e}")
            return False

    def get_all_payrolls(self) -> list:
        """Get all payroll records."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM payrolls ORDER BY created_at DESC')
            rows = cursor.fetchall()
            conn.close()
            return rows
        except Exception:
            return []

    def get_payrolls_by_employee(self, employee_id: int) -> list:
        """Get payroll records for an employee."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM payrolls WHERE employee_id = ? ORDER BY created_at DESC', (employee_id,))
            rows = cursor.fetchall()
            conn.close()
            return rows
        except Exception:
            return []

    def update_payroll(self, payroll_id: int, **kwargs):
        """Update payroll record."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            allowed = {
                'employee_id', 'period_start', 'period_end', 'base_salary', 'allowances', 'deductions',
                'overtime_hours', 'overtime_rate', 'gross_pay', 'net_pay', 'status', 'paid_date'
            }
            updates = []
            values = []
            for key, value in kwargs.items():
                if key in allowed and value is not None:
                    updates.append(f'{key} = ?')
                    values.append(value)
            if updates:
                updates.append('updated_at = CURRENT_TIMESTAMP')
                values.append(payroll_id)
                query = f'UPDATE payrolls SET {", ".join(updates)} WHERE id = ?'
                cursor.execute(query, values)
                conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating payroll: {e}")
            return False

    def delete_payroll(self, payroll_id: int):
        """Delete payroll record."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM payrolls WHERE id = ?', (payroll_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting payroll: {e}")
            return False

    # === APPRAISALS WORKFLOW ===

    def create_appraisal_cycle(self, employee_id: int, period_start: str, period_end: str, created_by: str = ""):
        """Create appraisal cycle."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute(
                '''
                INSERT INTO appraisal_cycles (employee_id, period_start, period_end, created_by)
                VALUES (?, ?, ?, ?)
                ''',
                (employee_id, period_start, period_end, created_by)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error creating appraisal: {e}")
            return False

    def get_all_appraisal_cycles(self) -> list:
        """Get all appraisal cycles."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM appraisal_cycles ORDER BY created_at DESC')
            rows = cursor.fetchall()
            conn.close()
            return rows
        except Exception:
            return []

    def update_appraisal_cycle(self, appraisal_id: int, **kwargs):
        """Update appraisal cycle."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            allowed = {
                'employee_id', 'period_start', 'period_end', 'status',
                'self_text', 'self_rating', 'manager_text', 'manager_rating', 'final_rating'
            }
            updates = []
            values = []
            for key, value in kwargs.items():
                if key in allowed and value is not None:
                    updates.append(f'{key} = ?')
                    values.append(value)
            if updates:
                updates.append('updated_at = CURRENT_TIMESTAMP')
                values.append(appraisal_id)
                query = f'UPDATE appraisal_cycles SET {", ".join(updates)} WHERE id = ?'
                cursor.execute(query, values)
                conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating appraisal: {e}")
            return False

    def create_feedback_request(self, appraisal_id: int, requester: str, target_employee_id: int, message: str = ""):
        """Create a 360 feedback request."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute(
                '''
                INSERT INTO feedback_requests (appraisal_id, requester, target_employee_id, message)
                VALUES (?, ?, ?, ?)
                ''',
                (appraisal_id, requester, target_employee_id, message)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error creating feedback request: {e}")
            return False

    def get_feedback_requests(self) -> list:
        """Get all feedback requests."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM feedback_requests ORDER BY created_at DESC')
            rows = cursor.fetchall()
            conn.close()
            return rows
        except Exception:
            return []

    def update_feedback_request(self, request_id: int, **kwargs):
        """Update feedback request."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            allowed = {'status', 'message'}
            updates = []
            values = []
            for key, value in kwargs.items():
                if key in allowed and value is not None:
                    updates.append(f'{key} = ?')
                    values.append(value)
            if updates:
                updates.append('updated_at = CURRENT_TIMESTAMP')
                values.append(request_id)
                query = f'UPDATE feedback_requests SET {", ".join(updates)} WHERE id = ?'
                cursor.execute(query, values)
                conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating feedback request: {e}")
            return False

    def add_feedback_entry(self, appraisal_id: int, from_employee_id: int, to_employee_id: int,
                           rating: float, feedback_text: str):
        """Add feedback entry."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute(
                '''
                INSERT INTO feedback_entries (appraisal_id, from_employee_id, to_employee_id, rating, feedback_text)
                VALUES (?, ?, ?, ?, ?)
                ''',
                (appraisal_id, from_employee_id, to_employee_id, rating, feedback_text)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding feedback: {e}")
            return False

    def get_feedback_entries(self) -> list:
        """Get all feedback entries."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM feedback_entries ORDER BY created_at DESC')
            rows = cursor.fetchall()
            conn.close()
            return rows
        except Exception:
            return []
    
    def add_appraisal(self, employee_id: int, appraisal_date: str, rating: str, comments: str):
        """Add employee appraisal."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO appraisals (employee_id, appraisal_date, rating, comments) VALUES (?, ?, ?, ?)',
                (employee_id, appraisal_date, rating, comments)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding appraisal: {e}")
            return False
    
    def get_employee_appraisals(self, employee_id: int) -> list:
        """Get all appraisals for an employee."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM appraisals WHERE employee_id = ? ORDER BY appraisal_date DESC', (employee_id,))
            rows = cursor.fetchall()
            conn.close()
            return rows
        except Exception:
            return []
    
    def add_goal(self, employee_id: int, goal: str, status: str, due_date: str, notes: str):
        """Add employee goal."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO goals (employee_id, goal, status, due_date, notes) VALUES (?, ?, ?, ?, ?)',
                (employee_id, goal, status, due_date, notes)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding goal: {e}")
            return False
    
    def get_employee_goals(self, employee_id: int) -> list:
        """Get all goals for an employee."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM goals WHERE employee_id = ? ORDER BY due_date', (employee_id,))
            rows = cursor.fetchall()
            conn.close()
            return rows
        except Exception:
            return []
    
    # === VISITORS ===
    
    def add_visitor(self, name: str, address: str, phone: str, email: str, company: str, notes: str):
        """Add new visitor."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO visitors (name, address, phone, email, company, notes) VALUES (?, ?, ?, ?, ?, ?)',
                (name, address, phone, email, company, notes)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding visitor: {e}")
            return False
    
    def get_all_visitors(self) -> list:
        """Get all visitors."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM visitors ORDER BY name')
            rows = cursor.fetchall()
            conn.close()
            return rows
        except Exception:
            return []
    
    def update_visitor(self, visitor_id: int, **kwargs):
        """Update visitor details."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            allowed_fields = {'name', 'address', 'phone', 'email', 'company', 'notes'}
            updates = []
            values = []
            
            for key, value in kwargs.items():
                if key in allowed_fields and value is not None:
                    updates.append(f'{key} = ?')
                    values.append(value)
            
            if updates:
                updates.append('updated_at = CURRENT_TIMESTAMP')
                values.append(visitor_id)
                query = f'UPDATE visitors SET {", ".join(updates)} WHERE id = ?'
                cursor.execute(query, values)
                conn.commit()
            
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating visitor: {e}")
            return False
    
    def delete_visitor(self, visitor_id: int):
        """Delete visitor."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM visitors WHERE id = ?', (visitor_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting visitor: {e}")
            return False
    
    def search_visitors(self, query: str) -> list:
        """Search visitors by name, email, phone."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            q = f"%{query}%"
            cursor.execute('SELECT * FROM visitors WHERE name LIKE ? OR email LIKE ? OR phone LIKE ? ORDER BY name', (q, q, q))
            rows = cursor.fetchall()
            conn.close()
            return rows
        except Exception:
            return []
    
    # === EMAIL CONFIG ===
    
    def save_email_config(self, smtp_server: str, smtp_port: int, sender_email: str,
                         sender_password: str, recipient_email: str):
        """Save email configuration."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM email_config')
            cursor.execute(
                'INSERT INTO email_config (smtp_server, smtp_port, sender_email, sender_password, recipient_email) VALUES (?, ?, ?, ?, ?)',
                (smtp_server, smtp_port, sender_email, sender_password, recipient_email)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving email config: {e}")
            return False
    
    def get_email_config(self) -> dict:
        """Get email configuration."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute('SELECT smtp_server, smtp_port, sender_email, sender_password, recipient_email FROM email_config LIMIT 1')
            row = cursor.fetchone()
            conn.close()
            if row:
                return {
                    'smtp_server': row[0], 'smtp_port': row[1], 'sender_email': row[2],
                    'sender_password': row[3], 'recipient_email': row[4]
                }
            return None
        except Exception:
            return None
    
    # === COMPANY INFO ===
    
    def save_company_info(self, company_name: str, address: str, phone: str,
                         email: str, tax_id: str, bank_details: str):
        """Save company information."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM company_info')
            cursor.execute(
                'INSERT INTO company_info (company_name, address, phone, email, tax_id, bank_details) VALUES (?, ?, ?, ?, ?, ?)',
                (company_name, address, phone, email, tax_id, bank_details)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving company info: {e}")
            return False
    
    def get_company_info(self) -> dict:
        """Get company information."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute('SELECT company_name, address, phone, email, tax_id, bank_details FROM company_info LIMIT 1')
            row = cursor.fetchone()
            conn.close()
            if row:
                return {
                    'company_name': row[0], 'address': row[1], 'phone': row[2],
                    'email': row[3], 'tax_id': row[4], 'bank_details': row[5]
                }
            return None
        except Exception:
            return None
    
    # === ACTIVITY LOG ===
    
    def log_activity(self, username: str, action: str, details: str = ""):
        """Log user activity."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO activity_log (username, action, details) VALUES (?, ?, ?)',
                (username, action, details)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error logging activity: {e}")
    
    def get_activity_log(self, username: str = None) -> list:
        """Get activity log, optionally filtered by user."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            if username:
                cursor.execute('SELECT * FROM activity_log WHERE username = ? ORDER BY timestamp DESC', (username,))
            else:
                cursor.execute('SELECT * FROM activity_log ORDER BY timestamp DESC')
            rows = cursor.fetchall()
            conn.close()
            return rows
        except Exception:
            return []
    
    def close(self):
        """Close database connection."""
        pass
