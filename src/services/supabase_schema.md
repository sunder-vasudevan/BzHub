# Supabase Table Mapping for BizHub

## Table Names and Fields

- users
  - id (uuid)
  - username (text)
  - password_hash (text)
  - role (text)
  - last_login (timestamp)

- inventory
  - id (uuid)
  - item_name (text)
  - quantity (int)
  - threshold (int)
  - cost_price (float)
  - sale_price (float)
  - description (text)
  - image_path (text)

- sales
  - id (uuid)
  - item_name (text)
  - quantity (int)
  - sale_price (float)
  - total_amount (float)
  - username (text)
  - date (timestamp)

- employees
  - id (uuid)
  - emp_number (text)
  - name (text)
  - joining_date (date)
  - designation (text)
  - manager (text)
  - team (text)
  - email (text)
  - phone (text)
  - emergency_contact (text)
  - photo_path (text)
  - notes (text)
  - is_active (int)

- appraisals
  - id (uuid)
  - employee_id (uuid)
  - appraisal_date (date)
  - rating (text)
  - comments (text)

- goals
  - id (uuid)
  - employee_id (uuid)
  - goal (text)
  - status (text)
  - due_date (date)
  - notes (text)

- visitors
  - id (uuid)
  - name (text)
  - address (text)
  - phone (text)
  - email (text)
  - company (text)
  - notes (text)

- email_config
  - id (uuid)
  - smtp_server (text)
  - smtp_port (int)
  - sender_email (text)
  - sender_password (text)
  - recipient_email (text)

- company_info
  - id (uuid)
  - company_name (text)
  - address (text)
  - phone (text)
  - email (text)
  - tax_id (text)
  - bank_details (text)

- activity_log
  - id (uuid)
  - username (text)
  - action (text)
  - details (text)
  - timestamp (timestamp)

- payroll
  - id (uuid)
  - employee_id (uuid)
  - period_start (date)
  - period_end (date)
  - base_salary (float)
  - allowances (float)
  - deductions (float)
  - overtime_hours (float)
  - overtime_rate (float)
  - gross_pay (float)
  - net_pay (float)
  - status (text)
  - paid_date (date)

- appraisal_cycles
  - id (uuid)
  - employee_id (uuid)
  - period_start (date)
  - period_end (date)
  - created_by (text)

- feedback_requests
  - id (uuid)
  - appraisal_id (uuid)
  - requester (text)
  - target_employee_id (uuid)
  - message (text)

- feedback_entries
  - id (uuid)
  - appraisal_id (uuid)
  - from_employee_id (uuid)
  - to_employee_id (uuid)
  - rating (float)
  - feedback_text (text)

---

This schema matches your BizHub app's requirements. Let me know if you want to customize any table or field names before I implement the sync logic.